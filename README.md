# 🐍 django_saas - SaaS Core Template (Backend)

Plantilla oficial y arquitectura base para sistemas SaaS Multitenant construida con **Django 6.0+**, **Django REST Framework** y **PostgreSQL**.

Incluye:
- 🏢 **Arquitectura Multitenant:** `TenantModelUUID` y `TenantModelID` con aislamiento estricto por organización.
- 🔐 **Autenticación JWT:** Módulo `uth/` con tokens de rotación, guards y roles (`ADMIN`, `OPERATOR`, `VIEWER`).
- 👥 **Módulos Core:** Organización (`org/`), Usuarios (`usr/`) y Seeds (`sed/`).
- 🤖 **Skills de IA integradas:** Carpeta `.agents/skills/` con `django-crud` para generar módulos de negocio.

## ⚡ Inicio Rápido
```bash
python -m venv env
# Windows: .\env\Scripts\activate | Linux/macOS: source env/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver 8000
```
