# Patrones de Código Canónicos para Django CRUD

### A. Modelo con UUID (Estándar Task)
```python
from django.db import models
from utl.models import TenantModelUUID

class {{Entity}}(TenantModelUUID):
  title = models.CharField(max_length=255)
  description = models.TextField(null=True, blank=True)

  class Meta:
    db_table = '{{Entity}}'
    ordering = ['-created_at']
```

### B. Modelo con Autoincrement (Estándar Paquete FastCargo)
```python
from django.db import models
from utl.models import TenantModelID

class {{Entity}}(TenantModelID):
  tracking = models.CharField(max_length=50)
  flete = models.FloatField(default=0)

  class Meta:
    db_table = '{{Entity}}'
    ordering = ['-created_at']
```

### C. Modelo con Shared PK (Estándar Declaracion FastCargo 1:1)
```python
from django.db import models
from utl.models import TenantBaseNoPK

class {{Entity}}(TenantBaseNoPK):
  paquete = models.OneToOneField(
    'pkg_gen.Paquete',
    on_delete=models.PROTECT,
    primary_key=True,
    related_name='{{entity_lower}}',
  )
  valor = models.FloatField(default=0)

  class Meta:
    db_table = '{{Entity}}'
```

### D. Modelo Global Sin Tenant (Estándar FaseCns / País)
```python
from django.db import models
from utl.models import GlobalModelID

class {{Entity}}(GlobalModelID):
  codigo = models.CharField(max_length=20, unique=True)
  nombre = models.CharField(max_length=100)

  class Meta:
    db_table = '{{Entity}}'
```

## 2. Plantilla de Serializers (`serializers.py`)

```python
from rest_framework import serializers
from utl.serializers import BaseTenantModelSerializer
from .models import {{Entity}}

class {{Entity}}Serializer(BaseTenantModelSerializer):
  class Meta(BaseTenantModelSerializer.Meta):
    model = {{Entity}}
    fields = [
      'id', 'organizacion_id', 'name', 'description', 'status',
      'is_active', 'created_at', 'updated_at', 'deleted_at',
    ]

class Create{{Entity}}Serializer(serializers.ModelSerializer):
  class Meta:
    model = {{Entity}}
    fields = ['name', 'description', 'status']

class Update{{Entity}}Serializer(serializers.ModelSerializer):
  name = serializers.CharField(max_length=255, required=False)
  description = serializers.CharField(allow_null=True, required=False, allow_blank=True)
  status = serializers.ChoiceField(choices={{Entity}}.STATUS_CHOICES, required=False)

  class Meta:
    model = {{Entity}}
    fields = ['name', 'description', 'status']
```

## 3. Plantilla de Vistas (`views.py`)

```python
from utl.generics import (
  TenantListAPIView, TenantDetailAPIView,
  TenantCreateAPIView, TenantUpdateAPIView,
  TenantSoftDeleteView, TenantRestoreView,
)
from utl.permissions import IsAdminRole
from .models import {{Entity}}
from .filter import {{Entity}}Filter
from .serializers import {{Entity}}Serializer, Create{{Entity}}Serializer, Update{{Entity}}Serializer

class {{Entity}}ListView(TenantListAPIView):
  queryset = {{Entity}}.objects.all()
  serializer_class = {{Entity}}Serializer
  filterset_class = {{Entity}}Filter

class {{Entity}}DetailView(TenantDetailAPIView):
  queryset = {{Entity}}.objects.all()
  serializer_class = {{Entity}}Serializer
  entity_name = "{{Entity}}"
  gender = "{{gender}}"

class {{Entity}}CreateView(TenantCreateAPIView):
  serializer_class = Create{{Entity}}Serializer
  response_serializer_class = {{Entity}}Serializer

class {{Entity}}UpdateView(TenantUpdateAPIView):
  queryset = {{Entity}}.objects.all()
  serializer_class = Update{{Entity}}Serializer
  response_serializer_class = {{Entity}}Serializer
  entity_name = "{{Entity}}"
  gender = "{{gender}}"

class {{Entity}}DeleteView(TenantSoftDeleteView):
  permission_classes = [TenantSoftDeleteView.permission_classes[0], IsAdminRole]
  queryset = {{Entity}}.objects.all()
  serializer_class = {{Entity}}Serializer
  entity_name = "{{Entity}}"
  gender = "{{gender}}"

class {{Entity}}RestoreView(TenantRestoreView):
  permission_classes = [TenantRestoreView.permission_classes[0], IsAdminRole]
  queryset = {{Entity}}.objects.all()
  serializer_class = {{Entity}}Serializer
  entity_name = "{{Entity}}"
  gender = "{{gender}}"
```
