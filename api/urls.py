from django.urls import re_path, include
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

class HealthCheckView(APIView):
  permission_classes = [AllowAny]

  def get(self, request, *args, **kwargs):
    return Response({
      'status': 'ok',
      'timestamp': timezone.now().isoformat(),
    })

urlpatterns = [
  re_path(r'^api/?$', HealthCheckView.as_view(), name='health-check-root'),
  re_path(r'^api/health/?$', HealthCheckView.as_view(), name='health-check'),
  re_path(r'^api/auth', include('mod.uth.urls')),
  re_path(r'^api/org', include('mod.org.urls')),
  re_path(r'^api/usr', include('mod.usr.urls')),
  re_path(r'^api/task', include('mod.tsk.urls')),
  re_path(r'^api/sed', include('mod.sed.urls')),
  re_path(r'^api', include('mod.sed.urls')),
]
