from rest_framework import serializers
from mod.usr.models import User

class LoginSerializer(serializers.Serializer):
  email = serializers.EmailField()
  password = serializers.CharField(write_only=True)

class UserMeSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['id', 'email', 'name', 'role', 'organizacion_id']
