from django.urls import re_path
from .views import (
  LoginView,
  MeView,
  RefreshView,
  LogoutView,
  CleanupBlacklistView,
)

urlpatterns = [
  re_path(r'^/login/?$', LoginView.as_view(), name='auth-login'),
  re_path(r'^/me/?$', MeView.as_view(), name='auth-me'),
  re_path(r'^/refresh/?$', RefreshView.as_view(), name='auth-refresh'),
  re_path(r'^/logout/?$', LogoutView.as_view(), name='auth-logout'),
  re_path(r'^/cleanup-blacklist/?$', CleanupBlacklistView.as_view(), name='auth-cleanup-blacklist'),
]
