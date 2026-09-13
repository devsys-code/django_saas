# Casos Avanzados en Django CRUD

## Caso 1: Registro Doble / Transacción Atómica (Persona + Usuario)

```python
from django.db import transaction
from rest_framework import serializers
from mod.usr.models import User
from .models import Persona

class CreatePersonaSerializer(serializers.ModelSerializer):
  email = serializers.EmailField(write_only=True)
  password = serializers.CharField(write_only=True)
  role = serializers.CharField(write_only=True, default='member')

  class Meta:
    model = Persona
    fields = ['first_name', 'last_name', 'dni', 'phone', 'email', 'password', 'role']

  def create(self, validated_data):
    email = validated_data.pop('email')
    password = validated_data.pop('password')
    role = validated_data.pop('role', 'member')
    organizacion = self.context['request'].user.organizacion

    with transaction.atomic():
      # 1. Crear usuario de autenticación
      user = User.objects.create_user(
        email=email,
        password=password,
        name=f"{validated_data.get('first_name', '')} {validated_data.get('last_name', '')}".strip(),
        role=role,
        organizacion=organizacion,
      )
      # 2. Crear persona asociada
      persona = Persona.objects.create(
        user=user,
        organizacion=organizacion,
        **validated_data
      )
      return persona
```

## Caso 2: Claves Primarias Autoincrementables

Si se usa clave primaria numérica (ej: `models.BigAutoField(primary_key=True)`):
1. Las expresiones regulares en `urls.py` deben capturar dígitos `(?P<id>\d+)` en vez de UUID `(?P<id>[0-9a-fA-F-]+)`.
2. Para simplificar, pasar el parámetro `id_pattern=r'\d+'` o definir `extra_urls` al llamar a `build_crud_urls`.

## Caso 3: Registro Masivo (Bulk Create)

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Paquete
from .serializers import CreatePaqueteSerializer, PaqueteSerializer

class PaqueteBulkCreateView(APIView):
  def post(self, request):
    serializer = CreatePaqueteSerializer(data=request.data, many=True)
    serializer.is_valid(raise_exception=True)
    
    paquetes = [
      Paquete(
        organizacion=request.user.organizacion,
        **item
      )
      for item in serializer.validated_data
    ]
    created = Paquete.objects.bulk_create(paquetes)
    return Response(PaqueteSerializer(created, many=True).data, status=status.HTTP_201_CREATED)
```
