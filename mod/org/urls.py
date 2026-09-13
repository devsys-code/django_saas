from django.urls import re_path
from utl.urls import build_crud_urls
from .views import (
  OrgListView,
  OrgDetailView,
  OrgCreateView,
  OrgUpdateView,
  OrgDeleteView,
  OrgRestoreView,
  OrgCheckSlugView,
)

extra_urls = [
  re_path(r'^/check-slug/(?P<slug>[^/]+)/?$', OrgCheckSlugView.as_view(), name='org-check-slug'),
]

urlpatterns = build_crud_urls(
  OrgListView,
  OrgDetailView,
  OrgCreateView,
  OrgUpdateView,
  OrgDeleteView,
  OrgRestoreView,
  extra_urls=extra_urls,
  prefix='org',
)
