from utl.exceptions import Conflict
from mod.uth.services import hash_password
from .models import User

def create_user_service(org_id: str, validated_data: dict) -> User:
  """Crea un usuario en el tenant validando unicidad de email y hasheando password."""
  email = validated_data['email']
  if User.objects.filter(organizacion_id=org_id, email=email).exists():
    raise Conflict(f'El email "{email}" ya está registrado en esta organización')

  password = validated_data['password']
  hashed_pw = hash_password(password)

  return User.objects.create(
    organizacion_id=org_id,
    email=email,
    name=validated_data['name'],
    password=hashed_pw,
    role=validated_data.get('role', 'member'),
  )

def update_user_service(instance: User, org_id: str, validated_data: dict) -> User:
  """Actualiza usuario en el tenant validando unicidad si cambia email y hasheando nuevo password."""
  new_email = validated_data.get('email')
  if new_email and new_email != instance.email:
    if User.objects.filter(organizacion_id=org_id, email=new_email).exclude(id=instance.id).exists():
      raise Conflict(f'El email "{new_email}" ya está registrado en esta organización')

  new_pw = validated_data.get('password')
  if new_pw:
    validated_data['password'] = hash_password(new_pw)

  for attr, value in validated_data.items():
    setattr(instance, attr, value)
  instance.save()
  return instance
