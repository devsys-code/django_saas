from datetime import datetime, timedelta, timezone as dt_timezone
from django.db import connection, transaction
from mod.uth.services import hash_password
from mod.org.models import Organizacion
from mod.usr.models import User
from mod.tsk.models import Task

ORGS = [
  {'name': 'TechCorp', 'slug': 'techcorp'},
  {'name': 'InnovateLab', 'slug': 'innovatelab'},
  {'name': 'DataSoft', 'slug': 'datasoft'},
  {'name': 'CloudNine', 'slug': 'cloudnine'},
  {'name': 'DigitalHub', 'slug': 'digitalhub'},
]

USERS_PER_ORG = [
  {'emailPrefix': 'admin', 'role': 'admin'},
  {'emailPrefix': 'user1', 'role': 'member'},
  {'emailPrefix': 'user2', 'role': 'member'},
  {'emailPrefix': 'user3', 'role': 'viewer'},
  {'emailPrefix': 'user4', 'role': 'member'},
]

ACTIONS = [
  'Revisar y corregir',
  'Implementar módulo de',
  'Optimizar rendimiento en',
  'Diseñar interfaz para',
  'Configurar pipeline de',
  'Escribir pruebas unitarias de',
  'Auditar seguridad y roles en',
  'Migrar base de datos de',
  'Documentar endpoints de',
  'Refactorizar lógica de negocio en',
  'Actualizar dependencias de',
  'Monitorear alertas en',
  'Automatizar despliegue de',
  'Integrar pasarela de',
]

TOPICS = [
  'autenticación JWT y roles de usuario',
  'pasarela de pagos con Stripe y Webhooks',
  'catálogo de productos e inventario',
  'notificaciones push y correos transaccionales',
  'gestión de pedidos y facturación electrónica',
  'caché distribuida con Redis y NestJS',
  'microservicio de envíos y geolocalización',
  'auditoría de eventos y logs estructurados',
  'dashboard de métricas en tiempo real',
  'exportación masiva de reportes en Excel y PDF',
  'control de acceso basado en políticas (PBAC)',
  'gestión de sesiones concurrentes y token blacklist',
  'subida y procesamiento de archivos multimedia',
  'sincronización de datos offline con clientes móviles',
]

MODULES = [
  'Auth',
  'Facturación',
  'Core API',
  'Seguridad',
  'Infraestructura',
  'Analytics',
  'Frontend UI',
  'Integraciones',
  'Reportes',
  'DevOps',
]

TICKET_PREFIXES = [
  'TECH',
  'FE',
  'BE',
  'CORE',
  'SEC',
  'DEVOPS',
  'DATA',
  'SRV',
]

STATUSES = ['yellow', 'green', 'red']

def get_title(seed_index: int, action: str, topic: str, prefix: str, num: int, mod: str) -> str:
  templates = [
    lambda: f"{action} {topic}",
    lambda: f"[{prefix}-{num}] {action} {topic}",
    lambda: f"{mod}: {action} {topic}",
    lambda: f"Feat: {action.lower()} {topic}",
    lambda: f"Fix: Error reportado al {action.lower()} {topic}",
    lambda: f"Refactor: {action} {topic} para v2.0",
    lambda: f"[Urgente] {action} {topic}",
    lambda: f"Integración: {action} {topic}",
    lambda: f"Ticket #{prefix}{num} - {action} {topic}",
    lambda: f"Auditoría: {action} {topic}",
  ]
  return templates[seed_index % len(templates)]()

def get_description(seed_index: int, action: str, topic: str, org_name: str) -> str | None:
  templates = [
    lambda: f"Se requiere {action.lower()} {topic} en el entorno de {org_name} para asegurar el cumplimiento de los estándares de calidad.",
    lambda: f"Prioridad alta para el sprint en curso. Es necesario {action.lower()} {topic} antes del siguiente release a producción.",
    lambda: f"Detalle técnico:\n- Objetivo principal: {action} {topic}.\n- Incluye validación de esquemas y pruebas de estrés.",
    lambda: f"El equipo de {org_name} reportó inconsistencias. Proceder con: {action.lower()} {topic}.",
    lambda: f"Pasos a seguir:\n1. Analizar requerimientos de arquitectura.\n2. {action} {topic}.\n3. Desplegar en staging para pruebas de integración.",
    lambda: f"Optimización solicitada tras revisión de logs. Alcance: {action.lower()} {topic}.",
    lambda: f"{topic[0].upper() + topic[1:]} pendiente de validación y pase a producción.",
    lambda: f"Revisar documentación técnica y coordinar con el equipo para {action.lower()} {topic}.",
    lambda: None,
  ]
  return templates[seed_index % len(templates)]()

def truncate_tables():
  with connection.cursor() as cursor:
    if connection.vendor == 'postgresql':
      cursor.execute('TRUNCATE TABLE "Task", "User", "Organizacion" RESTART IDENTITY CASCADE;')
    else:
      cursor.execute('DELETE FROM "Task";')
      cursor.execute('DELETE FROM "User";')
      cursor.execute('DELETE FROM "Organizacion";')

def run_seed():
  truncate_tables()
  hashed_password = hash_password('123456')

  total_orgs = 0
  total_users = 0
  total_tasks = 0

  now = datetime.now(dt_timezone.utc)

  with transaction.atomic():
    for org_idx, org_data in enumerate(ORGS):
      org = Organizacion.objects.create(name=org_data['name'], slug=org_data['slug'])
      total_orgs += 1

      for user_data in USERS_PER_ORG:
        User.objects.create(
          organizacion=org,
          email=f"{user_data['emailPrefix']}@{org_data['slug']}.com",
          name=f"{user_data['emailPrefix'].capitalize()} {org_data['name']}",
          password=hashed_password,
          role=user_data['role'],
        )
        total_users += 1

      tasks_to_create = []
      for i in range(1, 101):
        seed_index = org_idx * 100 + i

        action = ACTIONS[(seed_index * 7) % len(ACTIONS)]
        topic = TOPICS[(seed_index * 11) % len(TOPICS)]
        mod_name = MODULES[(seed_index * 3) % len(MODULES)]
        prefix = TICKET_PREFIXES[(seed_index * 5) % len(TICKET_PREFIXES)]
        ticket_num = 100 + ((seed_index * 13) % 900)

        title = get_title(seed_index, action, topic, prefix, ticket_num, mod_name)
        description = get_description(seed_index, action, topic, org_data['name'])

        status_val = STATUSES[(seed_index * 3) % len(STATUSES)]
        days_ago = (seed_index * 17) % 45
        seconds_offset = ((seed_index * 73) % 86400)
        created_at = now - timedelta(days=days_ago, seconds=seconds_offset)

        is_deleted = (i % 4 == 0)
        if is_deleted:
          del_hours = (((seed_index * 19) % 72) + 2)
          deleted_at = created_at + timedelta(hours=del_hours)
        else:
          deleted_at = None

        tasks_to_create.append(
          Task(
            organizacion=org,
            title=title,
            description=description,
            status=status_val,
            is_active=not is_deleted,
            created_at=created_at,
            updated_at=deleted_at or created_at,
            deleted_at=deleted_at,
          )
        )

      Task.objects.bulk_create(tasks_to_create)
      total_tasks += len(tasks_to_create)

  return {
    'message': 'Seed completado exitosamente',
    'organizaciones': total_orgs,
    'usuarios': total_users,
    'tareas': total_tasks,
    'credentials': {
      'note': 'Todas las contraseñas son: 123456',
      'users': [
        {
          'email': f"{u['emailPrefix']}@{o['slug']}.com",
          'password': '123456',
          'role': u['role'],
          'organizacion': o['name'],
        }
        for o in ORGS for u in USERS_PER_ORG
      ],
    },
  }

def run_reset():
  truncate_tables()
  return {
    'message': 'Tablas vaciadas y reiniciadas correctamente (Task, User, Organizacion)',
    'totalRemaining': 0,
  }
