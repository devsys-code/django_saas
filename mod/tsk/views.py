from utl.generics import (
  TenantListAPIView,
  TenantDetailAPIView,
  TenantCreateAPIView,
  TenantUpdateAPIView,
  TenantSoftDeleteView,
  TenantRestoreView,
)
from utl.permissions import IsAdminRole
from .models import Task
from .filter import TaskFilter
from .serializers import (
  TaskSerializer,
  CreateTaskSerializer,
  UpdateTaskSerializer,
)

class TaskListView(TenantListAPIView):
  queryset = Task.objects.all()
  serializer_class = TaskSerializer
  filterset_class = TaskFilter

class TaskDetailView(TenantDetailAPIView):
  queryset = Task.objects.all()
  serializer_class = TaskSerializer
  entity_name = "Tarea"
  gender = "f"

class TaskCreateView(TenantCreateAPIView):
  serializer_class = CreateTaskSerializer
  response_serializer_class = TaskSerializer

class TaskUpdateView(TenantUpdateAPIView):
  queryset = Task.objects.all()
  serializer_class = UpdateTaskSerializer
  response_serializer_class = TaskSerializer
  entity_name = "Tarea"
  gender = "f"

class TaskDeleteView(TenantSoftDeleteView):
  permission_classes = [TenantSoftDeleteView.permission_classes[0], IsAdminRole]
  queryset = Task.objects.all()
  serializer_class = TaskSerializer
  entity_name = "Tarea"
  gender = "f"

class TaskRestoreView(TenantRestoreView):
  permission_classes = [TenantRestoreView.permission_classes[0], IsAdminRole]
  queryset = Task.objects.all()
  serializer_class = TaskSerializer
  entity_name = "Tarea"
  gender = "f"
