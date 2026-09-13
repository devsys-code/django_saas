from django.urls import re_path

def build_crud_urls(
  list_v, detail_v, create_v, update_v, delete_v, restore_v,
  extra_urls=None, prefix='', id_pattern=r'[^/]+'
):
  """
  Generador escalonado de rutas canónicas para módulos CRUD de DRF.
  Estandariza los 6 endpoints por módulo reduciendo regex duplicados.
  Soporta UUIDs, IDs numéricos autoincrementables y códigos personalizados mediante id_pattern.
  """
  patterns = [
    re_path(r'^/?$', list_v.as_view(), name=f'{prefix}-list' if prefix else 'list'),
    re_path(rf'^/detail/(?P<id>{id_pattern})/?$', detail_v.as_view(), name=f'{prefix}-detail' if prefix else 'detail'),
    re_path(r'^/create/?$', create_v.as_view(), name=f'{prefix}-create' if prefix else 'create'),
    re_path(rf'^/update/(?P<id>{id_pattern})/?$', update_v.as_view(), name=f'{prefix}-update' if prefix else 'update'),
    re_path(rf'^/delete/(?P<id>{id_pattern})/?$', delete_v.as_view(), name=f'{prefix}-delete' if prefix else 'delete'),
    re_path(rf'^/restore/(?P<id>{id_pattern})/?$', restore_v.as_view(), name=f'{prefix}-restore' if prefix else 'restore'),
  ]
  return (extra_urls or []) + patterns
