from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from utl.models import TenantModel, TenantQuerySet

class UserManager(BaseUserManager):
  def create_user(self, email, name, password=None, organizacion=None, role='member', **extra_fields):
    if not email:
      raise ValueError('El email es obligatorio')
    email = self.normalize_email(email)
    user = self.model(
      email=email,
      name=name,
      organizacion=organizacion,
      role=role,
      **extra_fields
    )
    if password:
      user.set_password(password)
    else:
      user.set_unusable_password()
    user.save(using=self._db)
    return user

  def create_superuser(self, email, name, password=None, **extra_fields):
    extra_fields.setdefault('role', 'admin')
    return self.create_user(email, name, password, **extra_fields)

class User(AbstractBaseUser, TenantModel):
  ROLE_CHOICES = [
    ('admin', 'Admin'),
    ('member', 'Member'),
    ('viewer', 'Viewer'),
  ]

  email = models.CharField(max_length=255)
  name = models.CharField(max_length=255)
  password = models.CharField(max_length=255)
  role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='member')

  objects = UserManager.from_queryset(TenantQuerySet)()

  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = ['name']

  class Meta:
    db_table = 'User'
    unique_together = ('organizacion', 'email')
    ordering = ['-created_at']

  def __str__(self):
    return f"{self.email} ({self.role})"
