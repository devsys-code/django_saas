from rest_framework import serializers

class BaseAuditSerializer(serializers.ModelSerializer):
  """Escalón 1: Serializador con campos de auditoría estándar marcados como read-only."""
  class Meta:
    fields = ['id', 'is_active', 'created_at', 'updated_at', 'deleted_at']
    read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']

class BaseTenantModelSerializer(BaseAuditSerializer):
  """Escalón 2: Serializador multi-tenant que inyecta automáticamente el tenant en create."""
  class Meta:
    fields = ['id', 'organizacion_id', 'is_active', 'created_at', 'updated_at', 'deleted_at']
    read_only_fields = ['id', 'organizacion_id', 'created_at', 'updated_at', 'deleted_at']

  def create(self, validated_data):
    request = self.context.get('request')
    if request and hasattr(request, 'tenant') and 'organizacion_id' not in validated_data:
      if hasattr(self.Meta.model, 'organizacion') or hasattr(self.Meta.model, 'organizacion_id'):
        validated_data['organizacion_id'] = request.tenant.organizacion_id
    return super().create(validated_data)
