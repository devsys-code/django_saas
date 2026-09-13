import django_filters
from utl.filters import BaseFilterSet
from .models import Organizacion

class OrgFilter(BaseFilterSet):
  name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
  slug = django_filters.CharFilter(field_name='slug', lookup_expr='icontains')

  search_fields = ['name', 'slug']
  allowed_order_fields = [
    'id', 'name', 'slug', 'is_active',
    'created_at', 'updated_at', 'deleted_at',
  ]
  default_order_field = 'created_at'

  class Meta:
    model = Organizacion
    fields = [
      'id', 'name', 'slug', 'is_active', 'search',
      'created_at', 'created_at_gte', 'created_at_lte',
      'updated_at', 'updated_at_gte', 'updated_at_lte',
      'deleted_at', 'deleted_at_gte', 'deleted_at_lte',
    ]
