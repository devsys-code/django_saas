from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomPageNumberPagination(PageNumberPagination):
  """
  Paginador personalizado idéntico a Paginated<T> de NestJS.
  - page_query_param = 'page'
  - page_size_query_param = 'size' (con soporte fallback para 'page_size')
  - size == 0: retorna todos los registros sin dividir en páginas en el formato canónico
  - Enlaces first, last, next, previous como enteros o null (no URLs)
  """
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

