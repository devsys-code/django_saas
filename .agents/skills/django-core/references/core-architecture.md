# Código de Referencia Canónico: Django Core Architecture

## 1. `utl/models.py`
```python
import uuid
from django.db import models
from django.utils import timezone

class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        return self.update(is_deleted=True, deleted_at=timezone.now())

    def hard_delete(self):
        return super().delete()

    def alive(self):
        return self.filter(is_deleted=False)

    def dead(self):
        return self.filter(is_deleted=True)

class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).filter(is_deleted=False)

class TenantQuerySet(SoftDeleteQuerySet):
    def for_tenant(self, organizacion_id):
        if not organizacion_id:
            return self.none()
        return self.filter(organizacion_id=organizacion_id)

class TenantManager(models.Manager):
    def get_queryset(self):
        return TenantQuerySet(self.model, using=self._db).filter(is_deleted=False)

    def for_tenant(self, organizacion_id):
        return self.get_queryset().for_tenant(organizacion_id)

class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])

    def hard_delete(self, using=None, keep_parents=False):
        super().delete(using=using, keep_parents=keep_parents)

# 1. UUID PK + Tenant
class TenantModelUUID(SoftDeleteModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organizacion = models.ForeignKey(
        'org.Organizacion',
        on_delete=models.CASCADE,
        related_name='%(app_label)s_%(class)s_set',
        db_index=True
    )

    objects = TenantManager.from_queryset(TenantQuerySet)()

    class Meta:
        abstract = True

TenantModel = TenantModelUUID

# 2. BigAutoField Int PK + Tenant
class TenantModelID(SoftDeleteModel):
    id = models.BigAutoField(primary_key=True, editable=False)
    organizacion = models.ForeignKey(
        'org.Organizacion',
        on_delete=models.CASCADE,
        related_name='%(app_label)s_%(class)s_set',
        db_index=True
    )

    objects = TenantManager.from_queryset(TenantQuerySet)()

    class Meta:
        abstract = True

# 3. Base sin PK explicita (para 1:1 o PK compartida)
class TenantBaseNoPK(SoftDeleteModel):
    organizacion = models.ForeignKey(
        'org.Organizacion',
        on_delete=models.CASCADE,
        related_name='%(app_label)s_%(class)s_set',
        db_index=True
    )

    objects = TenantManager.from_queryset(TenantQuerySet)()

    class Meta:
        abstract = True

# 4. Modelos Globales
class GlobalModelID(SoftDeleteModel):
    id = models.BigAutoField(primary_key=True, editable=False)
    objects = SoftDeleteManager.from_queryset(SoftDeleteQuerySet)()

    class Meta:
        abstract = True

class GlobalModelUUID(SoftDeleteModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    objects = SoftDeleteManager.from_queryset(SoftDeleteQuerySet)()

    class Meta:
        abstract = True
```

## 2. `utl/generics.py`
```python
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

class TenantModelViewSet(viewsets.ModelViewSet):
    lookup_field = 'pk'
    lookup_url_kwarg = 'id'
    permission_classes = [permissions.IsAuthenticated]

    def get_tenant_id(self):
        user = self.request.user
        if hasattr(user, 'organizacion_id') and user.organizacion_id:
            return user.organizacion_id
        tenant_header = self.request.headers.get('X-Tenant-Id')
        if tenant_header:
            return tenant_header
        return None

    def get_queryset(self):
        qs = super().get_queryset()
        tenant_id = self.get_tenant_id()
        if hasattr(qs, 'for_tenant'):
            return qs.for_tenant(tenant_id)
        if hasattr(self.model, 'organizacion'):
            return qs.filter(organizacion_id=tenant_id)
        return qs

    def perform_create(self, serializer):
        tenant_id = self.get_tenant_id()
        if not tenant_id:
            raise PermissionDenied("Organización no identificada.")
        serializer.save(organizacion_id=tenant_id)
```

## 3. `utl/urls.py`
```python
from django.urls import re_path

def build_crud_urls(basename, viewset, id_pattern=r'[^/]+'):
    return [
        re_path(r'^$', viewset.as_view({'get': 'list', 'post': 'create'}), name=f'{basename}-list'),
        re_path(rf'^(?P<id>{id_pattern})/$', viewset.as_view({
            'get': 'retrieve',
            'put': 'update',
            'patch': 'partial_update',
            'delete': 'destroy'
        }), name=f'{basename}-detail'),
    ]
```
