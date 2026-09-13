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
