import django_filters
from utl.filters import BaseFilterSet
from .models import Task

class TaskFilter(BaseFilterSet):
  title = django_filters.CharFilter(field_name='title', lookup_expr='icontains')
  description = django_filters.CharFilter(field_name='description', lookup_expr='icontains')
  status = django_filters.ChoiceFilter(choices=Task.STATUS_CHOICES)

  search_fields = ['title', 'description']
  allowed_order_fields = [
    'id', 'title', 'description', 'status', 'is_active',
    'created_at', 'updated_at', 'deleted_at',
  ]
  default_order_field = 'created_at'

  class Meta:
    model = Task
    fields = [
      'id', 'title', 'description', 'status', 'is_active', 'search',
      'created_at', 'created_at_gte', 'created_at_lte',
      'updated_at', 'updated_at_gte', 'updated_at_lte',
      'deleted_at', 'deleted_at_gte', 'deleted_at_lte',
    ]
