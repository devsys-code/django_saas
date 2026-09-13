from utl.urls import build_crud_urls
from .views import (
  TaskListView,
  TaskDetailView,
  TaskCreateView,
  TaskUpdateView,
  TaskDeleteView,
  TaskRestoreView,
)

urlpatterns = build_crud_urls(
  TaskListView,
  TaskDetailView,
  TaskCreateView,
  TaskUpdateView,
  TaskDeleteView,
  TaskRestoreView,
  prefix='task',
)
