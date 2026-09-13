from rest_framework import exceptions

class TenantResourceMixin:
  """
  Mixin para Vistas Basadas en Clases Genéricas de DRF que estandariza:
  1. Filtrado automático por tenant (request.tenant.organizacion_id).
  2. Búsqueda de objeto get_object() con mensajes 404 canónicos idénticos a NestJS:
     '{entity_name} con id "{id}" no encontrado/a'.
  3. Soporte opcional para requerir que la entidad no esté eliminada lógicamente (require_not_deleted = True).
  """
  entity_name = "Recurso"
  gender = "m"  # 'm' o 'f'
  tenant_field = "organizacion_id"  # 'id' para Organizacion, 'organizacion_id' para User y Task
  require_not_deleted = False

  def get_tenant_id(self):
    tenant = getattr(self.request, 'tenant', None)
    return getattr(tenant, 'organizacion_id', None)

  def get_queryset(self):
    qs = super().get_queryset()
    tenant_id = self.get_tenant_id()
    if tenant_id and self.tenant_field:
      qs = qs.filter(**{self.tenant_field: tenant_id})
    if getattr(self, 'require_not_deleted', False):
      qs = qs.filter(deleted_at__isnull=True)
    return qs

  def get_object(self):
    lookup_url_kwarg = getattr(self, 'lookup_url_kwarg', None) or self.lookup_field
    lookup_val = self.kwargs.get(lookup_url_kwarg)
    term = "no encontrada" if self.gender == "f" else "no encontrado"

    try:
      queryset = self.filter_queryset(self.get_queryset())
      obj = queryset.get(**{self.lookup_field: lookup_val})
      self.check_object_permissions(self.request, obj)
      return obj
    except Exception:
      raise exceptions.NotFound(f'{self.entity_name} con id "{lookup_val}" {term}')
