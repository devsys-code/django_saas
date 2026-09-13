# Suite Completa de Infraestructura y Utilitarios (`utl/`) - Django 6.0+

Este documento contiene la implementación exacta de los 11 archivos de infraestructura de `utl/` para replicar el 100% de la arquitectura SaaS en cualquier proyecto Django nuevo.

---

## 1. `utl/models.py`
```python
import uuid
from django.db import models
from django.utils import timezone

class SoftDeleteQuerySet(models.QuerySet):
  def delete(self):
    return self.update(is_deleted=True, deleted_at=timezone.now(), is_active=False)

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
  is_active = models.BooleanField(default=True, db_index=True)
  deleted_at = models.DateTimeField(null=True, blank=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  objects = SoftDeleteManager()
  all_objects = models.Manager()

  class Meta:
    abstract = True

  def delete(self, using=None, keep_parents=False):
    self.is_deleted = True
    self.is_active = False
    self.deleted_at = timezone.now()
    self.save(update_fields=['is_deleted', 'is_active', 'deleted_at', 'updated_at'])

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

---

## 2. `utl/authentication.py`
```python
import jwt
from django.conf import settings
from django.utils import timezone
from rest_framework import authentication, exceptions

class TenantContext:
  def __init__(self, organizacion_id: str, user_id: str, email: str, role: str):
    self.organizacion_id = str(organizacion_id)
    self.user_id = str(user_id)
    self.email = email
    self.role = role

class JWTAuthentication(authentication.BaseAuthentication):
  def authenticate(self, request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
      return None

    token = auth_header.split(' ')[1].strip()
    if not token:
      return None

    secret = getattr(settings, 'JWT_SECRET', 'super-secret-jwt-key-2026')

    try:
      payload = jwt.decode(token, secret, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
      raise exceptions.AuthenticationFailed('Token expirado')
    except jwt.InvalidTokenError:
      raise exceptions.AuthenticationFailed('Token inválido')

    jti = payload.get('jti')
    user_id = payload.get('sub')
    org_id = payload.get('organizacion_id')
    role = payload.get('role')

    if not user_id or not jti:
      raise exceptions.AuthenticationFailed('Token inválido')

    from mod.uth.models import TokenBlacklist
    if TokenBlacklist.objects.filter(jti=jti, expired_at__gt=timezone.now()).exists():
      raise exceptions.AuthenticationFailed('Token invalidado (sesión cerrada)')

    from mod.usr.models import User
    try:
      user = User.objects.get(id=user_id, deleted_at__isnull=True)
    except User.DoesNotExist:
      raise exceptions.AuthenticationFailed('Usuario no registrado')

    if not user.is_active:
      raise exceptions.AuthenticationFailed('Usuario inactivo')

    request.tenant = TenantContext(
      organizacion_id=org_id or str(user.organizacion_id),
      user_id=str(user.id),
      email=user.email,
      role=role or user.role,
    )

    return (user, token)

  def authenticate_header(self, request):
    return 'Bearer'
```

---

## 3. `utl/pagination.py`
```python
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomPageNumberPagination(PageNumberPagination):
  page_query_param = 'page'
  page_size_query_param = 'size'
  page_size = 10
  max_page_size = None

  def get_page_size(self, request):
    size_param = request.query_params.get(self.page_size_query_param)
    if size_param is None:
      size_param = request.query_params.get('page_size')
    if size_param is not None:
      try:
        val = int(size_param)
        if val >= 0:
          return val
      except (TypeError, ValueError):
        pass
    return self.page_size

  def paginate_queryset(self, queryset, request, view=None):
    self.request = request
    page_size = self.get_page_size(request)
    self.page_size_val = page_size

    if page_size == 0:
      self.total_count = queryset.count() if hasattr(queryset, 'count') else len(queryset)
      self.is_unpaginated = True
      return list(queryset)

    self.is_unpaginated = False
    return super().paginate_queryset(queryset, request, view)

  def get_paginated_response(self, data):
    if getattr(self, 'is_unpaginated', False):
      count = self.total_count
      first = 1 if count > 0 else None
      return Response({
        'count': count,
        'page': 1,
        'size': 0,
        'page_size': 0,
        'first': first,
        'last': None,
        'next': None,
        'previous': None,
        'results': data,
      })

    total = self.page.paginator.count
    first = 1 if total > 0 else None
    last = self.page.paginator.num_pages if total > 0 else None
    next_page = self.page.next_page_number() if self.page.has_next() else None
    prev_page = self.page.previous_page_number() if self.page.has_previous() else None
    current_page = self.page.number
    actual_size = self.page_size_val or self.page_size

    return Response({
      'count': total,
      'page': current_page,
      'size': actual_size,
      'page_size': actual_size,
      'first': first,
      'last': last,
      'next': next_page,
      'previous': prev_page,
      'results': data,
    })
```

---

## 4. `utl/filters.py`
```python
import django_filters
from django.db.models import Q

class BaseInFilter(django_filters.BaseInFilter, django_filters.CharFilter):
  pass

class BaseFilterSet(django_filters.FilterSet):
  search = django_filters.CharFilter(method='filter_search_declarative')
  id = BaseInFilter(field_name='id', lookup_expr='in')
  is_active = django_filters.BooleanFilter(field_name='is_active')

  created_at = django_filters.DateFilter(field_name='created_at', lookup_expr='date')
  created_at_gte = django_filters.DateFilter(field_name='created_at', lookup_expr='date__gte')
  created_at_lte = django_filters.DateFilter(field_name='created_at', lookup_expr='date__lte')

  updated_at = django_filters.DateFilter(field_name='updated_at', lookup_expr='date')
  updated_at_gte = django_filters.DateFilter(field_name='updated_at', lookup_expr='date__gte')
  updated_at_lte = django_filters.DateFilter(field_name='updated_at', lookup_expr='date__lte')

  deleted_at = django_filters.DateFilter(field_name='deleted_at', lookup_expr='date')
  deleted_at_gte = django_filters.DateFilter(field_name='deleted_at', lookup_expr='date__gte')
  deleted_at_lte = django_filters.DateFilter(field_name='deleted_at', lookup_expr='date__lte')

  def filter_search_declarative(self, queryset, name, value):
    if not value:
      return queryset
    fields = getattr(self, 'search_fields', [])
    if not fields:
      return queryset
    query = Q()
    for field in fields:
      query |= Q(**{f"{field}__icontains": value})
    return queryset.filter(query)

  def filter_queryset(self, queryset):
    qs = super().filter_queryset(queryset)

    has_deleted_filter = (
      'deleted_at' in self.data or
      'deleted_at_gte' in self.data or
      'deleted_at_lte' in self.data
    )
    is_explicitly_inactive = str(self.data.get('is_active', '')).lower() == 'false'

    if not has_deleted_filter and not is_explicitly_inactive:
      qs = qs.filter(deleted_at__isnull=True)

    order_by = self.data.get('order_by')
    order_dir = self.data.get('order_dir', 'desc').lower()

    allowed_order_fields = getattr(self, 'allowed_order_fields', ['created_at'])
    default_order_field = getattr(self, 'default_order_field', 'created_at')

    target_field = order_by if order_by in allowed_order_fields else default_order_field
    prefix = '' if order_dir == 'asc' else '-'

    return qs.order_by(f"{prefix}{target_field}")
```

---

## 5. `utl/exceptions.py`
```python
import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException
from django.http import Http404
from django.core.exceptions import PermissionDenied

logger = logging.getLogger(__name__)

class Conflict(APIException):
  status_code = status.HTTP_409_CONFLICT
  default_detail = 'Conflicto con el estado actual del recurso'
  default_code = 'conflict'

def _flatten_errors(detail):
  if isinstance(detail, list):
    if len(detail) == 1:
      return _flatten_errors(detail[0])
    return [_flatten_errors(item) for item in detail]
  if isinstance(detail, dict):
    messages = []
    for field, errors in detail.items():
      flat = _flatten_errors(errors)
      if isinstance(flat, list):
        for f in flat:
          messages.append(f"{field}: {f}" if field != 'non_field_errors' else str(f))
      else:
        messages.append(f"{field}: {flat}" if field != 'non_field_errors' else str(flat))
    return messages[0] if len(messages) == 1 else messages
  return str(detail)

def custom_exception_handler(exc, context):
  response = exception_handler(exc, context)

  if response is not None:
    status_code = response.status_code
    detail = response.data
    if isinstance(detail, dict):
      if 'detail' in detail:
        msg = _flatten_errors(detail['detail'])
      elif 'message' in detail:
        msg = detail['message']
      else:
        msg = _flatten_errors(detail)
    else:
      msg = _flatten_errors(detail)

    return Response(
      {
        "statusCode": status_code,
        "message": msg,
      },
      status=status_code,
    )

  if isinstance(exc, Http404):
    return Response(
      {
        "statusCode": status.HTTP_404_NOT_FOUND,
        "message": str(exc) or "Recurso no encontrado",
      },
      status=status.HTTP_404_NOT_FOUND,
    )

  if isinstance(exc, PermissionDenied):
    return Response(
      {
        "statusCode": status.HTTP_403_FORBIDDEN,
        "message": str(exc) or "Permiso denegado",
      },
      status=status.HTTP_403_FORBIDDEN,
    )

  logger.error("Unhandled Exception: %s", exc, exc_info=True)
  return Response(
    {
      "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
      "message": "Error interno del servidor",
    },
    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
  )
```

---

## 6. `utl/permissions.py`
```python
from rest_framework.permissions import BasePermission

class IsAuthenticatedTenant(BasePermission):
  def has_permission(self, request, view):
    return bool(
      request.user and
      request.user.is_authenticated and
      request.user.is_active and
      request.user.deleted_at is None and
      getattr(request, 'tenant', None) is not None
    )

class IsAdminRole(BasePermission):
  def has_permission(self, request, view):
    if not (request.user and request.user.is_authenticated):
      return False
    tenant = getattr(request, 'tenant', None)
    return bool(tenant and tenant.role == 'admin')
```

---

## 7. `utl/mixins.py`
```python
from rest_framework import exceptions

class TenantResourceMixin:
  entity_name = "Recurso"
  gender = "m"
  tenant_field = "organizacion_id"
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
```

---

## 8. `utl/soft_delete.py`
```python
from django.utils import timezone
from rest_framework import generics, status, exceptions
from rest_framework.response import Response

class BaseSoftDeleteView(generics.UpdateAPIView):
  entity_name = "Recurso"
  gender = "m"
  lookup_field = 'id'

  def get_object(self):
    lookup_val = self.kwargs.get(self.lookup_field)
    term = "no encontrada" if self.gender == 'f' else "no encontrado"
    try:
      obj = self.get_queryset().get(**{self.lookup_field: lookup_val})
      self.check_object_permissions(self.request, obj)
      return obj
    except Exception:
      raise exceptions.NotFound(f'{self.entity_name} con id "{lookup_val}" {term}')

  def perform_update(self, serializer):
    serializer.instance.deleted_at = timezone.now()
    serializer.instance.is_active = False
    serializer.save()

  def delete(self, request, *args, **kwargs):
    instance = self.get_object()
    if instance.deleted_at is not None:
      term = "no encontrada" if self.gender == 'f' else "no encontrado"
      raise exceptions.NotFound(f'{self.entity_name} con id "{instance.id}" {term}')

    serializer = self.get_serializer(instance, data={}, partial=True)
    serializer.is_valid(raise_exception=True)
    self.perform_update(serializer)

    term_elim = "eliminada" if self.gender == 'f' else "eliminado"
    return Response(
      {"message": f"{self.entity_name} {term_elim} correctamente"},
      status=status.HTTP_200_OK,
    )

  def patch(self, request, *args, **kwargs):
    return self.delete(request, *args, **kwargs)

class BaseRestoreView(generics.UpdateAPIView):
  entity_name = "Recurso"
  gender = "m"
  lookup_field = 'id'

  def get_queryset(self):
    return super().get_queryset().all()

  def get_object(self):
    lookup_val = self.kwargs.get(self.lookup_field)
    term = "no encontrada o no eliminada" if self.gender == 'f' else "no encontrado o no eliminado"
    try:
      obj = self.get_queryset().get(**{self.lookup_field: lookup_val})
      self.check_object_permissions(self.request, obj)
      return obj
    except Exception:
      raise exceptions.NotFound(f'{self.entity_name} con id "{lookup_val}" {term}')

  def perform_update(self, serializer):
    serializer.instance.deleted_at = None
    serializer.instance.is_active = True
    serializer.save()

  def patch(self, request, *args, **kwargs):
    instance = self.get_object()
    if instance.deleted_at is None:
      term = "no encontrada o no eliminada" if self.gender == 'f' else "no encontrado o no eliminado"
      raise exceptions.NotFound(f'{self.entity_name} con id "{instance.id}" {term}')

    serializer = self.get_serializer(instance, data={}, partial=True)
    serializer.is_valid(raise_exception=True)
    self.perform_update(serializer)

    term_rest = "restaurada" if self.gender == 'f' else "restaurado"
    return Response(
      {"message": f"{self.entity_name} {term_rest} correctamente"},
      status=status.HTTP_200_OK,
    )
```

---

## 9. `utl/serializers.py`
```python
from rest_framework import serializers

class BaseAuditSerializer(serializers.ModelSerializer):
  class Meta:
    fields = ['id', 'is_active', 'created_at', 'updated_at', 'deleted_at']
    read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']

class BaseTenantModelSerializer(BaseAuditSerializer):
  class Meta:
    fields = ['id', 'organizacion_id', 'is_active', 'created_at', 'updated_at', 'deleted_at']
    read_only_fields = ['id', 'organizacion_id', 'created_at', 'updated_at', 'deleted_at']

  def create(self, validated_data):
    request = self.context.get('request')
    if request and hasattr(request, 'tenant') and 'organizacion_id' not in validated_data:
      if hasattr(self.Meta.model, 'organizacion') or hasattr(self.Meta.model, 'organizacion_id'):
        validated_data['organizacion_id'] = request.tenant.organizacion_id
    return super().create(validated_data)
```

---

## 10. `utl/urls.py`
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

---

## 11. `utl/generics.py`
```python
from rest_framework import viewsets, permissions
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
    tenant = getattr(self.request, 'tenant', None)
    if tenant:
      return getattr(tenant, 'organizacion_id', None)
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
