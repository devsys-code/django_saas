from utl.urls import build_crud_urls
from .views import (
  UsrListView,
  UsrDetailView,
  UsrCreateView,
  UsrUpdateView,
  UsrDeleteView,
  UsrRestoreView,
)

urlpatterns = build_crud_urls(
  UsrListView,
  UsrDetailView,
  UsrCreateView,
  UsrUpdateView,
  UsrDeleteView,
  UsrRestoreView,
  prefix='usr',
)
