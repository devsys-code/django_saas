from rest_framework import generics, exceptions, status
from rest_framework.response import Response
from utl.permissions import IsAuthenticatedTenant
from utl.pagination import CustomPageNumberPagination
from utl.mixins import TenantResourceMixin
from utl.soft_delete import BaseSoftDeleteView, BaseRestoreView

class TenantListAPIView(TenantResourceMixin, generics.ListAPIView):
  """Escalón 1: Vista genérica de listado aislada por tenant y con paginación canónica."""
  permission_classes = [IsAuthenticatedTenant]
  pagination_class = CustomPageNumberPagination

class TenantDetailAPIView(TenantResourceMixin, generics.RetrieveAPIView):
  """Escalón 2: Vista genérica de detalle aislada por tenant con mensajes 404 canónicos y resolución de PK dinámica."""
  permission_classes = [IsAuthenticatedTenant]
  lookup_field = 'pk'
  lookup_url_kwarg = 'id'

class TenantCreateAPIView(generics.CreateAPIView):
  """Escalón 3: Vista genérica de creación con auto-asignación de tenant y soporte para response_serializer_class."""
  permission_classes = [IsAuthenticatedTenant]
  response_serializer_class = None

  def perform_create(self, serializer):
    tenant = getattr(self.request, 'tenant', None)
    model = getattr(serializer.Meta, 'model', None)
    if tenant and model and (hasattr(model, 'organizacion_id') or hasattr(model, 'organizacion')):
      serializer.save(organizacion_id=tenant.organizacion_id)
    else:
      serializer.save()

  def create(self, request, *args, **kwargs):
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    self.perform_create(serializer)
    resp_cls = getattr(self, 'response_serializer_class', None)
    data = resp_cls(serializer.instance).data if resp_cls else serializer.data
    headers = self.get_success_headers(serializer.data)
    return Response(data, status=status.HTTP_201_CREATED, headers=headers)

class TenantUpdateAPIView(TenantResourceMixin, generics.UpdateAPIView):
  """Escalón 4: Vista genérica de actualización parcial aislada por tenant con soporte para response_serializer_class."""
  permission_classes = [IsAuthenticatedTenant]
  lookup_field = 'pk'
  lookup_url_kwarg = 'id'
  require_not_deleted = True
  response_serializer_class = None

  def update(self, request, *args, **kwargs):
    partial = kwargs.pop('partial', True)
    instance = self.get_object()
    serializer = self.get_serializer(instance, data=request.data, partial=partial)
    serializer.is_valid(raise_exception=True)
    self.perform_update(serializer)
    resp_cls = getattr(self, 'response_serializer_class', None)
    data = resp_cls(instance).data if resp_cls else serializer.data
    return Response(data, status=status.HTTP_200_OK)

class TenantSoftDeleteView(TenantResourceMixin, BaseSoftDeleteView):
  """Escalón 5: Vista genérica de soft delete (DELETE) aislada por tenant."""
  permission_classes = [IsAuthenticatedTenant]
  lookup_field = 'pk'
  lookup_url_kwarg = 'id'

class TenantRestoreView(TenantResourceMixin, BaseRestoreView):
  """Escalón 6: Vista genérica de restore (PATCH) aislada por tenant."""
  permission_classes = [IsAuthenticatedTenant]
  lookup_field = 'pk'
  lookup_url_kwarg = 'id'

  def get_object(self):
    lookup_val = self.kwargs.get(self.lookup_url_kwarg or self.lookup_field)
    term = "no encontrada o no eliminada" if self.gender == 'f' else "no encontrado o no eliminado"
    try:
      obj = self.get_queryset().get(pk=lookup_val)
      self.check_object_permissions(self.request, obj)
      return obj
    except Exception:
      raise exceptions.NotFound(f'{self.entity_name} con id "{lookup_val}" {term}')
