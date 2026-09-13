from django.conf import settings
from rest_framework import generics, status, exceptions
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .services import run_seed, run_reset

class SeedView(generics.GenericAPIView):
  permission_classes = [AllowAny]

  def get(self, request, *args, **kwargs):
    if not getattr(settings, 'DEBUG', True):
      raise exceptions.PermissionDenied('Operación no permitida en producción')
    result = run_seed()
    return Response(result, status=status.HTTP_200_OK)

class ResetView(generics.GenericAPIView):
  permission_classes = [AllowAny]

  def get(self, request, *args, **kwargs):
    if not getattr(settings, 'DEBUG', True):
      raise exceptions.PermissionDenied('Operación no permitida en producción')
    result = run_reset()
    return Response(result, status=status.HTTP_200_OK)
