from rest_framework import serializers
from utl.serializers import BaseAuditSerializer
from .models import Organizacion

class OrgSerializer(BaseAuditSerializer):
  class Meta(BaseAuditSerializer.Meta):
    model = Organizacion
    fields = [
      'id', 'name', 'slug', 'is_active',
      'created_at', 'updated_at', 'deleted_at',
    ]

class CreateUserInOrgSerializer(serializers.Serializer):
  email = serializers.EmailField()
  name = serializers.CharField(max_length=255)
  password = serializers.CharField(min_length=6, write_only=True)

class CreateOrgSerializer(serializers.Serializer):
  name = serializers.CharField(max_length=255)
  slug = serializers.CharField(max_length=100)
  user = CreateUserInOrgSerializer()

  def validate_slug(self, value):
    return value.strip().lower()

class UpdateOrgSerializer(serializers.ModelSerializer):
  name = serializers.CharField(max_length=255, required=False)
  slug = serializers.CharField(max_length=100, required=False)
  is_active = serializers.BooleanField(required=False)

  class Meta:
    model = Organizacion
    fields = ['name', 'slug', 'is_active']

  def validate_slug(self, value):
    return value.strip().lower()
