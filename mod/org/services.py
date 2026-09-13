from django.db import transaction
from utl.exceptions import Conflict
from mod.uth.services import hash_password
from mod.usr.models import User
from .models import Organizacion

def create_org_with_admin(validated_data: dict) -> dict:
  name = validated_data['name']
  slug = validated_data['slug'].strip().lower()
  user_data = validated_data['user']

  if Organizacion.objects.filter(slug=slug).exists():
    raise Conflict(f'El slug "{slug}" ya está en uso')

  with transaction.atomic():
    org = Organizacion.objects.create(name=name, slug=slug)

    hashed_pw = hash_password(user_data['password'])
    user = User.objects.create(
      organizacion=org,
      email=user_data['email'],
      name=user_data['name'],
      password=hashed_pw,
      role='admin',
    )

    return {
      'organizacion': {
        'id': str(org.id),
        'name': org.name,
        'slug': org.slug,
        'is_active': org.is_active,
        'created_at': org.created_at.isoformat(),
        'updated_at': org.updated_at.isoformat(),
      },
      'user': {
        'id': str(user.id),
        'email': user.email,
        'name': user.name,
        'role': user.role,
      },
    }

def check_slug_availability(slug: str) -> dict:
  clean_slug = slug.strip().lower()
  if not Organizacion.objects.filter(slug=clean_slug).exists():
    return {'available': True}

  counter = 1
  suggestion = f"{clean_slug}-{counter}"
  while Organizacion.objects.filter(slug=suggestion).exists() and counter <= 10:
    counter += 1
    suggestion = f"{clean_slug}-{counter}"

  return {'available': False, 'suggestion': suggestion}

def update_org_service(instance: Organizacion, validated_data: dict) -> Organizacion:
  """Actualiza la organización validando unicidad si cambia el slug."""
  new_slug = validated_data.get('slug')
  if new_slug:
    clean_slug = new_slug.strip().lower()
    if Organizacion.objects.filter(slug=clean_slug).exclude(id=instance.id).exists():
      raise Conflict(f'El slug "{clean_slug}" ya está en uso')
    validated_data['slug'] = clean_slug

  for attr, value in validated_data.items():
    setattr(instance, attr, value)
  instance.save()
  return instance

