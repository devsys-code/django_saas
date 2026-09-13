from django.urls import re_path
from .views import SeedView, ResetView

urlpatterns = [
  re_path(r'^/?seed/?$', SeedView.as_view(), name='seed'),
  re_path(r'^/?reset/?$', ResetView.as_view(), name='reset'),
]
