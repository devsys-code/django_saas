from rest_framework.permissions import BasePermission

class IsAuthenticatedTenant(BasePermission):
  """Permite el acceso únicamente a usuarios autenticados con contexto de organización."""
  def has_permission(self, request, view):
    return bool(
      request.user and
      request.user.is_authenticated and
      request.user.is_active and
      request.user.deleted_at is None and
      getattr(request, 'tenant', None) is not None
    )

class IsAdminRole(BasePermission):
  """Permite el acceso únicamente a usuarios con rol 'admin'."""
  def has_permission(self, request, view):
    if not (request.user and request.user.is_authenticated):
      return False
    tenant = getattr(request, 'tenant', None)
    return bool(tenant and tenant.role == 'admin')
