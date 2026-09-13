import uuid
from datetime import datetime, timedelta, timezone as dt_timezone
import bcrypt
import jwt
from django.conf import settings
from django.utils import timezone
from rest_framework import exceptions
from .models import RefreshToken, TokenBlacklist

def calculate_next_sunday_3am() -> datetime:
  """Calcula la fecha y hora exacta del próximo domingo a las 03:00 AM UTC."""
  now = datetime.now(dt_timezone.utc)
  weekday = now.weekday()
  if weekday == 6 and (now.hour < 3):
    days_ahead = 0
  else:
    days_ahead = (6 - weekday) % 7 or 7

  target = now + timedelta(days=days_ahead)
  next_sunday = target.replace(hour=3, minute=0, second=0, microsecond=0)
  if next_sunday <= now:
    next_sunday += timedelta(days=7)
  return next_sunday

def seconds_until(target_date: datetime) -> int:
  now = datetime.now(dt_timezone.utc)
  delta = target_date - now
  return max(int(delta.total_seconds()), 0)

def hash_password(password: str) -> str:
  salt = bcrypt.gensalt(rounds=10)
  return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def check_password_hash(raw_password: str, hashed_password: str) -> bool:
  try:
    return bcrypt.checkpw(raw_password.encode('utf-8'), hashed_password.encode('utf-8'))
  except Exception:
    return False

def generate_tokens(user):
  secret = getattr(settings, 'JWT_SECRET', 'super-secret-jwt-key-2026')
  now = datetime.now(dt_timezone.utc)

  # Access Token (15m por defecto)
  access_jti = str(uuid.uuid4())
  access_exp = now + timedelta(minutes=15)
  access_payload = {
    'sub': str(user.id),
    'email': user.email,
    'organizacion_id': str(user.organizacion_id),
    'role': user.role,
    'jti': access_jti,
    'exp': int(access_exp.timestamp()),
  }
  access_token = jwt.encode(access_payload, secret, algorithm='HS256')

  # Refresh Token (hasta el próximo domingo a las 03:00 AM)
  refresh_jti = str(uuid.uuid4())
  expires_at = calculate_next_sunday_3am()
  refresh_payload = {
    'sub': str(user.id),
    'jti': refresh_jti,
    'exp': int(expires_at.timestamp()),
  }
  refresh_token = jwt.encode(refresh_payload, secret, algorithm='HS256')

  RefreshToken.objects.create(
    jti=refresh_jti,
    user_id=str(user.id),
    expires_at=expires_at,
  )

  return access_token, refresh_token

def set_refresh_cookie(response, refresh_token: str):
  expires_at = calculate_next_sunday_3am()
  max_age = seconds_until(expires_at)
  is_prod = not getattr(settings, 'DEBUG', True)
  response.set_cookie(
    key='refreshToken',
    value=refresh_token,
    max_age=max_age,
    httponly=True,
    path='/',
    samesite='Strict' if is_prod else 'Lax',
    secure=is_prod,
  )

def clear_refresh_cookie(response):
  is_prod = not getattr(settings, 'DEBUG', True)
  response.set_cookie(
    key='refreshToken',
    value='',
    max_age=0,
    httponly=True,
    path='/',
    samesite='Strict' if is_prod else 'Lax',
    secure=is_prod,
  )

def extract_refresh_token_from_request(request) -> str | None:
  return request.COOKIES.get('refreshToken')

def refresh_tokens(refresh_token_str: str):
  secret = getattr(settings, 'JWT_SECRET', 'super-secret-jwt-key-2026')
  try:
    payload = jwt.decode(refresh_token_str, secret, algorithms=['HS256'])
  except jwt.PyJWTError:
    raise exceptions.AuthenticationFailed('Refresh token inválido o expirado')

  jti = payload.get('jti')
  user_id = payload.get('sub')
  if not jti or not user_id:
    raise exceptions.AuthenticationFailed('Refresh token inválido')

  try:
    token_record = RefreshToken.objects.get(jti=jti)
  except RefreshToken.DoesNotExist:
    raise exceptions.AuthenticationFailed('Refresh token no encontrado')

  if token_record.revoked:
    raise exceptions.AuthenticationFailed('Refresh token revocado')

  if token_record.expires_at <= timezone.now():
    raise exceptions.AuthenticationFailed('Refresh token expirado')

  from mod.usr.models import User
  try:
    user = User.objects.get(id=user_id, deleted_at__isnull=True, is_active=True)
  except User.DoesNotExist:
    raise exceptions.AuthenticationFailed('Usuario no encontrado')

  new_access_token, new_refresh_token = generate_tokens(user)
  new_refresh_payload = jwt.decode(new_refresh_token, secret, algorithms=['HS256'])

  token_record.revoked = True
  token_record.replaced_by = new_refresh_payload.get('jti')
  token_record.save(update_fields=['revoked', 'replaced_by'])

  return new_access_token, new_refresh_token

def logout_user(access_token_str: str, refresh_token_str: str | None = None):
  secret = getattr(settings, 'JWT_SECRET', 'super-secret-jwt-key-2026')
  try:
    payload = jwt.decode(access_token_str, secret, algorithms=['HS256'], options={"verify_exp": False})
    jti = payload.get('jti')
    sub = payload.get('sub')
    exp = payload.get('exp')

    if jti and sub and exp:
      expired_at = datetime.fromtimestamp(exp, tz=dt_timezone.utc)
      TokenBlacklist.objects.get_or_create(
        jti=jti,
        defaults={'user_id': sub, 'expired_at': expired_at}
      )
  except Exception:
    pass

  if refresh_token_str:
    try:
      r_payload = jwt.decode(refresh_token_str, secret, algorithms=['HS256'], options={"verify_exp": False})
      r_jti = r_payload.get('jti')
      if r_jti:
        RefreshToken.objects.filter(jti=r_jti, revoked=False).update(revoked=True)
    except Exception:
      pass

def clean_expired_blacklist() -> int:
  deleted_count, _ = TokenBlacklist.objects.filter(expired_at__lt=timezone.now()).delete()
  return deleted_count

def clean_expired_refresh_tokens() -> int:
  deleted_count, _ = RefreshToken.objects.filter(expires_at__lt=timezone.now()).delete()
  return deleted_count
