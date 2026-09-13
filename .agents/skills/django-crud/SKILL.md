---
name: django-crud
description: >-
  Genera módulos CRUD completos y repetitivos en Django 6.0+ y Django REST Framework (DRF) con PostgreSQL,
  soporte para jerarquía de modelos TenantModel/SoftDeleteModel, claves primarias UUID/autoincrement,
  transacciones atómicas (transaction.atomic), registro masivo, validación y registro automático
  en api/settings.py y api/urls.py, y generación de contratos de handoff para Frontend.
  Trigger cuando el usuario solicite crear módulos o APIs en Django siguiendo el estándar de Task.
---

# Django 6 CRUD Generator & Automation Skill

Este skill automatiza de manera integral y estandarizada la generación de módulos CRUD para **Django 6.0+** / DRF en `bck_dj/`, basándose en el patrón canónico implementado en `bck_dj/mod/tsk/` y los utilitarios de `bck_dj/utl/`.

---

## 1. Cuadro de Referencia Rápida

| Componente | Ubicación en el Proyecto | Hereda / Extiende | Propósito |
| :--- | :--- | :--- | :--- |
| **Model** | `bck_dj/mod/<cat_3>/<sub_3>/models.py` | `TenantModelUUID` / `TenantModelID` / `TenantBaseNoPK` / `GlobalModelID` | Modelo según estrategia de PK (UUID, Autoincremental, Shared PK o Global) |
| **Serializers** | `bck_dj/mod/<cat_3>/<sub_3>/serializers.py` | `BaseTenantModelSerializer` | Serialización DRF de lectura, creación y actualización |
| **Filtros** | `bck_dj/mod/<cat_3>/<sub_3>/filter.py` | `BaseFilterSet` | Filtros dinámicos con `django-filter` |
| **Vistas** | `bck_dj/mod/<cat_3>/<sub_3>/views.py` | `Tenant*APIView` | Vistas genéricas canónicas (List, Detail, Create, Update, Delete, Restore) |
| **URLs** | `bck_dj/mod/<cat_3>/<sub_3>/urls.py` | `build_crud_urls` | Rutas estandarizadas sin regex duplicados |
| **AppConfig** | `bck_dj/mod/<cat_3>/<sub_3>/apps.py` | `AppConfig` | Configuración de la aplicación Django |
| **Central Settings** | `bck_dj/api/settings.py` | — | Registro en `INSTALLED_APPS` |
| **Central URLs** | `bck_dj/api/urls.py` | — | Inclusión de rutas en `urlpatterns` |

---

## 2. Entradas Requeridas del Desarrollador

```markdown
- Entidad / Modelo: [Ej: Paquete / Persona]
- Plural: [Ej: Paquetes / Personas]
- Género Gramatical: ['m' | 'f'] (para mensajes "creado/creada con éxito")
- Carpeta (Regla de 3 letras): [Ej: log/paq o usr/per o tsk]
- Clave Primaria: [uuid (default) | autoincrement | custom_name (ej: user_id)]
- Multi-Tenant: [true (default) | false]
- Atributos:
  - nombre_campo: tipo Django (CharField, DecimalField, DateTimeField, etc.), opciones (null, blank, max_length, default)
- Relaciones: [ej: ForeignKey con Organizacion, OneToOneField con User]
- Casos Especiales:
  - Registro Doble: [si/no - modelo sincronizado]
  - Registro Masivo: [si/no]
  - Endpoints Estadísticos: [si/no]
```

---

## 3. Protocolo de Ejecución Paso a Paso

### Paso 1: Crear Módulo y `apps.py`
Crear directorio `bck_dj/mod/<cat_3>/<sub_3>/` y archivo `apps.py`:
```python
from django.apps import AppConfig

class {{Name}}Config(AppConfig):
  default_auto_field = 'django.db.models.BigAutoField'
  name = 'mod.{{cat_3}}.{{sub_3}}'
```

### Paso 2: Crear `models.py`
Heredar de `TenantModel` (desde `utl.models`). Definir `class Meta: db_table = '{{Entity}}'; ordering = ['-created_at']`.

### Paso 3: Crear `serializers.py`
- `{{Entity}}Serializer(BaseTenantModelSerializer)`: Contiene campos de auditoría (`id`, `organizacion_id`, `created_at`, etc.).
- `Create{{Entity}}Serializer(serializers.ModelSerializer)`: Campos editables para creación.
- `Update{{Entity}}Serializer(serializers.ModelSerializer)`: Campos con `required=False`.

### Paso 4: Crear `filter.py`
Heredar de `BaseFilterSet` (desde `utl.filters`). Configurar `search_fields` y `allowed_order_fields`.

### Paso 5: Crear `views.py`
Implementar las 6 vistas estándar con `TenantListAPIView`, `TenantDetailAPIView`, `TenantCreateAPIView`, `TenantUpdateAPIView`, `TenantSoftDeleteView`, `TenantRestoreView`.

### Paso 6: Crear `urls.py`
Usar `build_crud_urls` con el prefijo canónico:
```python
from utl.urls import build_crud_urls
from .views import *

urlpatterns = build_crud_urls(
  {{Entity}}ListView, {{Entity}}DetailView, {{Entity}}CreateView,
  {{Entity}}UpdateView, {{Entity}}DeleteView, {{Entity}}RestoreView,
  prefix='{{slug}}',
)
```

### Paso 7: Validación y Registro Central
1. Añadir `'mod.{{cat_3}}.{{sub_3}}.apps.{{Name}}Config'` a `INSTALLED_APPS` en `bck_dj/api/settings.py`.
2. Añadir `re_path(r'^api/{{slug}}', include('mod.{{cat_3}}.{{sub_3}}.urls'))` a `bck_dj/api/urls.py`.

### Paso 8: Comandos de Migración
Generar y aplicar migraciones:
```powershell
python manage.py makemigrations {{sub_3}}
python manage.py migrate {{sub_3}}
```

### Paso 9: Generación de Documentación y Contrato
1. `doc/backend/{{sub_3}}_django_backend.md`
2. `doc/contracts/{{sub_3}}_frontend_handoff.md`

---

## 4. Auditoría y Buenas Prácticas Django

- Cumplimiento de PEP 8.
- Optimización con `select_related` y `prefetch_related` para claves foráneas.
- Aislamiento estricto de queries con `TenantQuerySet.for_tenant(organizacion_id)`.

---

## 5. Referencias y Guías Detalladas

- Consulta `references/patterns.md` para ver las plantillas de código completas.
- Consulta `references/advanced-cases.md` para casos de transacciones atómicas `transaction.atomic()` y claves autoincrementables.
