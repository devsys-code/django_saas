---
name: django-core
description: >-
  Genera la arquitectura base e infraestructura de backend en Django 6.0+ y DRF para sistemas SaaS multitenant desde cero, incluyendo clases abstractas de modelos (TenantModelUUID, TenantModelID, TenantBaseNoPK, GlobalModelID, GlobalModelUUID, SoftDeleteModel), vistas genericas TenantModelViewSet, enrutamiento dinamico build_crud_urls, autenticacion JWT, configuracion de settings y modulos estandar Organizacion y Usuario. Trigger cuando se solicite inicializar, configurar o generar la base o core de un backend Django SaaS desde cero.
---

# Django 6.0+ SaaS Core Skill

Esta skill genera y estandariza la **capa de infraestructura y arquitectura base** para proyectos backend en Django 6.0+ con Django REST Framework (DRF) y PostgreSQL, sin generar entidades de negocio (que corresponden a `django-crud`).

---

## 1. Responsabilidades de la Skill

Al ejecutarse en un proyecto nuevo o existente, garantiza que el backend cuente con:
1. **Modelos Abstractos Multitenant** (`utl/models.py`):
   - `TenantModelUUID`: Para tablas estándar con PK UUID y campo `organizacion`.
   - `TenantModelID`: Para tablas con PK autoincremental (`BigAutoField`) y campo `organizacion`.
   - `TenantBaseNoPK`: Para tablas 1:1 o con claves compuestas donde la PK es foránea a otro modelo.
   - `GlobalModelID` / `GlobalModelUUID`: Para tablas compartidas de catálogo global (sin tenant).
   - `SoftDeleteModel` y `TenantQuerySet`: Borrado lógico y filtrado automático por tenant.
2. **Genéricos y Vistas Base** (`utl/generics.py`):
   - `TenantModelViewSet`: ViewSet con `lookup_field = 'pk'` y `lookup_url_kwarg = 'id'`, compatible con UUID y enteros.
   - Paginación estándar DRF: `{ "count": N, "next": "...", "previous": "...", "results": [...] }`.
3. **Enrutamiento Dinámico** (`utl/urls.py`):
   - `build_crud_urls` con regex `r'[^/]+'` para admitir cualquier formato de identificador.
4. **Módulos Core del SaaS**:
   - `mod/org`: Modelo `Organizacion` (nombre, slug, logo, configuración).
   - `mod/usr`: Modelo `User` multitenant con roles (`admin`, `member`, `viewer`), `UserManager` y validación de unicidad por organización.
   - `mod/uth`: Autenticación JWT (`/api/v1/auth/login/`, `/api/v1/auth/refresh/`, `/api/v1/auth/me/`) devolviendo el tenant activo y permisos.
5. **Configuración del Sistema** (`api/settings.py`):
   - CORS habilitado para frontends (Angular y React).
   - Middleware de detección de Tenant vía header `X-Tenant-Id` o token JWT.
   - Autenticación `rest_framework_simplejwt`.

---

## 2. Protocolo de Ejecución Paso a Paso

### Paso 1: Estructura de Directorios
Verificar o crear la estructura estándar:
```text
bck_dj/
├── api/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── mod/
│   ├── __init__.py
│   ├── org/
│   ├── usr/
│   └── uth/
├── utl/
│   ├── __init__.py
│   ├── generics.py
│   ├── models.py
│   └── urls.py
├── manage.py
└── requirements.txt
```

### Paso 2: Generar Utilitarios de Infraestructura (`utl/`)
Consultar el archivo de referencia `references/core-architecture.md` para implementar:
- `utl/models.py`
- `utl/generics.py`
- `utl/urls.py`

### Paso 3: Generar Módulos SaaS Fundacionales
- `mod/org`: Modelo `Organizacion` heredando de `SoftDeleteModel`.
- `mod/usr`: Modelo `User` heredando de `AbstractBaseUser` y `TenantModel`.
- `mod/uth`: Vistas de Login JWT que retornan el objeto de usuario completo con su `organizacion_id` y su `role`.

### Paso 4: Configurar `api/settings.py` y `api/urls.py`
Registrar las aplicaciones en `INSTALLED_APPS`, configurar `AUTH_USER_MODEL = 'usr.User'`, y registrar las rutas core:
- `/api/v1/auth/` -> Login, Refresh, Me.
- `/api/v1/org/` -> CRUD de Organizaciones.
- `/api/v1/usr/` -> CRUD de Usuarios del Tenant.

### Paso 5: Verificación
Ejecutar:
```powershell
python manage.py check
```

---

## 3. Contrato de Salida para Frontend (Interoperable)

Las APIs generadas por este core devuelven:
- **Login Response (`/api/v1/auth/login/`)**:
  ```json
  {
    "access": "jwt_token_here",
    "refresh": "refresh_token_here",
    "user": {
      "id": "uuid-or-id",
      "email": "user@org.com",
      "name": "Juan Perez",
      "role": "admin",
      "organizacion": {
        "id": "uuid-org",
        "name": "Mi Empresa",
        "slug": "mi-empresa"
      }
    }
  }
  ```
- **Listados DRF (`/api/v1/<recurso>/`)**:
  ```json
  {
    "count": 42,
    "next": "http://.../?page=2",
    "previous": null,
    "results": [ ... ]
  }
  ```
- **Cabeceras Aceptadas**:
  - `Authorization: Bearer <token>`
  - `X-Tenant-Id: <uuid-organizacion>`
