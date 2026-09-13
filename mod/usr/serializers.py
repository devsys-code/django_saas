from rest_framework import serializers
from utl.serializers import BaseTenantModelSerializer
from .models import User

class UserSerializer(BaseTenantModelSerializer):
  class Meta(BaseTenantModelSerializer.Meta):
    model = User
    fields = [
      'id', 'organizacion_id', 'email', 'name', 'role',
      'is_active', 'created_at', 'updated_at', 'deleted_at',
    ]

class CreateUserSerializer(serializers.ModelSerializer):
  password = serializers.CharField(min_length=6, write_only=True)

  class Meta:
    model = User
    fields = ['email', 'name', 'password', 'role']

class UpdateUserSerializer(serializers.ModelSerializer):
  email = serializers.EmailField(required=False)
  name = serializers.CharField(max_length=255, required=False)
  password = serializers.CharField(min_length=6, write_only=True, required=False)
  role = serializers.ChoiceField(choices=User.ROLE_CHOICES, required=False)
  is_active = serializers.BooleanField(required=False)

  class Meta:
    model = User
    fields = ['email', 'name', 'password', 'role', 'is_active']
