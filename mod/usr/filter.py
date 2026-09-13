import django_filters
from utl.filters import BaseFilterSet
from .models import User

class UsrFilter(BaseFilterSet):
  email = django_filters.CharFilter(field_name='email', lookup_expr='icontains')
  name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
  role = django_filters.CharFilter(field_name='role', lookup_expr='icontains')

  search_fields = ['email', 'name']
  allowed_order_fields = [
    'id', 'email', 'name', 'role', 'is_active',
    'created_at', 'updated_at', 'deleted_at',
  ]
  default_order_field = 'created_at'

  class Meta:
    model = User
    fields = [
      'id', 'email', 'name', 'role', 'is_active', 'search',
      'created_at', 'created_at_gte', 'created_at_lte',
      'updated_at', 'updated_at_gte', 'updated_at_lte',
      'deleted_at', 'deleted_at_gte', 'deleted_at_lte',
    ]
