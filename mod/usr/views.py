from rest_framework import status
from rest_framework.response import Response
from utl.generics import (
  TenantListAPIView,
  TenantDetailAPIView,
  TenantCreateAPIView,
  TenantUpdateAPIView,
  TenantSoftDeleteView,
  TenantRestoreView,
)
from utl.permissions import IsAdminRole
from .models import User
from .filter import UsrFilter
from .serializers import (
  UserSerializer,
  CreateUserSerializer,
  UpdateUserSerializer,
)
from .services import create_user_service, update_user_service

class UsrListView(TenantListAPIView):
  queryset = User.objects.all()
  serializer_class = UserSerializer
  filterset_class = UsrFilter

class UsrDetailView(TenantDetailAPIView):
  queryset = User.objects.all()
  serializer_class = UserSerializer
  entity_name = "Usuario"
  gender = "m"

class UsrCreateView(TenantCreateAPIView):
  permission_classes = [TenantCreateAPIView.permission_classes[0], IsAdminRole]
  serializer_class = CreateUserSerializer

  def create(self, request, *args, **kwargs):
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = create_user_service(request.tenant.organizacion_id, serializer.validated_data)
    return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

class UsrUpdateView(TenantUpdateAPIView):
  permission_classes = [TenantUpdateAPIView.permission_classes[0], IsAdminRole]
  queryset = User.objects.all()
  serializer_class = UpdateUserSerializer
  entity_name = "Usuario"
  gender = "m"

  def update(self, request, *args, **kwargs):
    instance = self.get_object()
    serializer = self.get_serializer(instance, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    user = update_user_service(instance, request.tenant.organizacion_id, serializer.validated_data)
    return Response(UserSerializer(user).data, status=status.HTTP_200_OK)

class UsrDeleteView(TenantSoftDeleteView):
  permission_classes = [TenantSoftDeleteView.permission_classes[0], IsAdminRole]
  queryset = User.objects.all()
  serializer_class = UserSerializer
  entity_name = "Usuario"
  gender = "m"

class UsrRestoreView(TenantRestoreView):
  permission_classes = [TenantRestoreView.permission_classes[0], IsAdminRole]
  queryset = User.objects.all()
  serializer_class = UserSerializer
  entity_name = "Usuario"
  gender = "m"
