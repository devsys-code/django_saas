from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from utl.permissions import IsAdminRole
from utl.generics import (
  TenantListAPIView,
  TenantDetailAPIView,
  TenantUpdateAPIView,
  TenantSoftDeleteView,
  TenantRestoreView,
)
from .models import Organizacion
from .filter import OrgFilter
from .serializers import (
  OrgSerializer,
  CreateOrgSerializer,
  UpdateOrgSerializer,
)
from .services import (
  create_org_with_admin,
  check_slug_availability,
  update_org_service,
)

class OrgCreateView(generics.CreateAPIView):
  permission_classes = [AllowAny]
  serializer_class = CreateOrgSerializer

  def create(self, request, *args, **kwargs):
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    result = create_org_with_admin(serializer.validated_data)
    return Response(result, status=status.HTTP_201_CREATED)

class OrgCheckSlugView(generics.GenericAPIView):
  permission_classes = [AllowAny]

  def get(self, request, slug, *args, **kwargs):
    result = check_slug_availability(slug)
    return Response(result, status=status.HTTP_200_OK)

class OrgListView(TenantListAPIView):
  queryset = Organizacion.objects.all()
  serializer_class = OrgSerializer
  filterset_class = OrgFilter
  tenant_field = 'id'

class OrgDetailView(TenantDetailAPIView):
  queryset = Organizacion.objects.all()
  serializer_class = OrgSerializer
  entity_name = "Organización"
  gender = "f"
  tenant_field = 'id'

class OrgUpdateView(TenantUpdateAPIView):
  permission_classes = [TenantUpdateAPIView.permission_classes[0], IsAdminRole]
  queryset = Organizacion.objects.all()
  serializer_class = UpdateOrgSerializer
  entity_name = "Organización"
  gender = "f"
  tenant_field = 'id'

  def update(self, request, *args, **kwargs):
    instance = self.get_object()
    serializer = self.get_serializer(instance, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    org = update_org_service(instance, serializer.validated_data)
    return Response(OrgSerializer(org).data, status=status.HTTP_200_OK)

class OrgDeleteView(TenantSoftDeleteView):
  permission_classes = [TenantSoftDeleteView.permission_classes[0], IsAdminRole]
  queryset = Organizacion.objects.all()
  serializer_class = OrgSerializer
  entity_name = "Organización"
  gender = "f"
  tenant_field = 'id'

class OrgRestoreView(TenantRestoreView):
  permission_classes = [TenantRestoreView.permission_classes[0], IsAdminRole]
  queryset = Organizacion.objects.all()
  serializer_class = OrgSerializer
  entity_name = "Organización"
  gender = "f"
  tenant_field = 'id'
