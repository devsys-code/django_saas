from rest_framework import serializers
from utl.serializers import BaseTenantModelSerializer
from .models import Task

class TaskSerializer(BaseTenantModelSerializer):
  class Meta(BaseTenantModelSerializer.Meta):
    model = Task
    fields = [
      'id', 'organizacion_id', 'title', 'description', 'status',
      'is_active', 'created_at', 'updated_at', 'deleted_at',
    ]

class CreateTaskSerializer(serializers.ModelSerializer):
  class Meta:
    model = Task
    fields = ['title', 'description', 'status']

class UpdateTaskSerializer(serializers.ModelSerializer):
  title = serializers.CharField(max_length=255, required=False)
  description = serializers.CharField(allow_null=True, required=False, allow_blank=True)
  status = serializers.ChoiceField(choices=Task.STATUS_CHOICES, required=False)

  class Meta:
    model = Task
    fields = ['title', 'description', 'status']
