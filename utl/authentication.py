import jwt
from django.conf import settings
from django.utils import timezone
from rest_framework import authentication, exceptions

class TenantContext:
  def __init__(self, organizacion_id: str, user_id: str, email: str, role: str):
    self.organizacion_id = str(organizacion_id)
    self.user_id = str(user_id)
    self.email = email
    self.role = role

class JWTAuthentication(authentication.BaseAuthentication):
  def authenticate(self, request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
      return None

    token = auth_header.split(' ')[1].strip()
    if not token:
      return None

    secret = getattr(settings, 'JWT_SECRET', 'super-secret-jwt-key-2026')

    try:
      payload = jwt.decode(token, secret, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
      raise exceptions.AuthenticationFailed('Token expirado')
    except jwt.InvalidTokenError:
      raise exceptions.AuthenticationFailed('Token inválido')

    jti = payload.get('jti')
    user_id = payload.get('sub')
    org_id = payload.get('organizacion_id')
    role = payload.get('role')

    if not user_id or not jti:
      raise exceptions.AuthenticationFailed('Token inválido')

    # Verificar si el token está en la lista negra
    from mod.uth.models import TokenBlacklist
    if TokenBlacklist.objects.filter(jti=jti, expired_at__gt=timezone.now()).exists():
      raise exceptions.AuthenticationFailed('Token invalidado (sesión cerrada)')

    # Obtener el usuario en la base de datos
    from mod.usr.models import User
    try:
      user = User.objects.get(id=user_id, deleted_at__isnull=True)
    except User.DoesNotExist:
      raise exceptions.AuthenticationFailed('Usuario no registrado')

    if not user.is_active:
      raise exceptions.AuthenticationFailed('Usuario inactivo')

    request.tenant = TenantContext(
      organizacion_id=org_id or str(user.organizacion_id),
      user_id=str(user.id),
      email=user.email,
      role=role or user.role,
    )

    return (user, token)

  def authenticate_header(self, request):
    return 'Bearer'
