import uuid
from django.db import models
from django.utils import timezone

class TimeStampedModel(models.Model):
  """Auditoría temporal: Marcas de tiempo de creación y actualización automática sin imponer clave primaria."""
  created_at = models.DateTimeField(default=timezone.now)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    abstract = True

class SoftDeleteQuerySet(models.QuerySet):
  """QuerySet con soporte para filtrado de registros activos o eliminados lógicamente."""
  def active(self):
    return self.filter(deleted_at__isnull=True, is_active=True)

  def deleted(self):
    return self.filter(deleted_at__isnull=False)

class SoftDeleteModel(TimeStampedModel):
  """Eliminación lógica: Hereda timestamps pero tampoco impone clave primaria."""
  is_active = models.BooleanField(default=True)
  deleted_at = models.DateTimeField(null=True, blank=True)

  objects = SoftDeleteQuerySet.as_manager()

  class Meta:
    abstract = True

class TenantQuerySet(SoftDeleteQuerySet):
  """QuerySet con soporte adicional para aislamiento multi-tenant."""
  def for_tenant(self, organizacion_id):
    return self.filter(organizacion_id=organizacion_id)

class TenantMixin(models.Model):
  """Mixin para aislamiento multi-tenant obligatorio asociado a una Organización."""
  organizacion = models.ForeignKey(
    'org.Organizacion',
    on_delete=models.RESTRICT,
    db_column='organizacion_id',
    related_name='%(class)ss',
  )

  objects = TenantQuerySet.as_manager()

  class Meta:
    abstract = True

# -----------------------------------------------------------------------------
# MODELOS MULTI-TENANT SEGÚN ESTRATEGIA DE CLAVE PRIMARIA
# -----------------------------------------------------------------------------

class TenantModelUUID(SoftDeleteModel, TenantMixin):
  """Modelo Multi-Tenant con clave primaria UUIDv4 (por defecto en Task)."""
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  objects = TenantQuerySet.as_manager()

  class Meta:
    abstract = True

# Alias canónico para mantener retrocompatibilidad total con código existente:
TenantModel = TenantModelUUID

class TenantModelID(SoftDeleteModel, TenantMixin):
  """Modelo Multi-Tenant con clave primaria autoincremental BigAutoField (ej: Paquete en FastCargo)."""
  id = models.BigAutoField(primary_key=True)
  objects = TenantQuerySet.as_manager()

  class Meta:
    abstract = True

class TenantBaseNoPK(SoftDeleteModel, TenantMixin):
  """Modelo Multi-Tenant sin clave primaria predefinida (para Shared PK como OneToOneField(primary_key=True))."""
  objects = TenantQuerySet.as_manager()

  class Meta:
    abstract = True

# -----------------------------------------------------------------------------
# MODELOS GLOBALES (SIN TENANT / CATÁLOGOS COMPARTIDOS)
# -----------------------------------------------------------------------------

class GlobalModelID(SoftDeleteModel):
  """Modelo global del sistema con clave autoincremental BigAutoField."""
  id = models.BigAutoField(primary_key=True)

  class Meta:
    abstract = True

class GlobalModelUUID(SoftDeleteModel):
  """Modelo global del sistema con clave UUIDv4."""
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

  class Meta:
    abstract = True

# Mantenimiento de clase legada para compatibilidad
class UUIDBaseModel(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  class Meta:
    abstract = True
