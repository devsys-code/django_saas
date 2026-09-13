import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')
django.setup()

from rest_framework.test import APIClient

client = APIClient()

def run_tests():
  print("=== INICIANDO SUITE DE PRUEBAS DE BCK_DJ ===")

  # 1. Health Check
  res = client.get('/api/')
  assert res.status_code == 200, f"Health root failed: {res.status_code}"
  assert res.json()['status'] == 'ok'

  res_h = client.get('/api/health')
  assert res_h.status_code == 200, f"Health explicit failed: {res_h.status_code}"
  assert res_h.json()['status'] == 'ok'
  print("1. Health Check (root /api/ y /api/health) [PASS]")

  # 2. Seed (tanto canónico /api/seed como /api/sed/seed)
  res = client.get('/api/seed')
  assert res.status_code == 200, f"Seed canónico failed: {res.status_code}"
  seed_data = res.json()
  assert seed_data['organizaciones'] == 5
  assert seed_data['usuarios'] == 25
  assert seed_data['tareas'] == 500
  print("2. Seed canónico (/api/seed): 5 orgs, 25 users, 500 tasks [PASS]")

  # 3. Login
  login_payload = {
    'email': 'admin@techcorp.com',
    'password': '123456',
  }
  res = client.post('/api/auth/login', login_payload, format='json')
  assert res.status_code == 201, f"Login failed: {res.status_code} {res.json()}"
  login_data = res.json()
  assert 'access_token' in login_data
  assert login_data['user']['role'] == 'admin'
  assert 'refreshToken' in res.cookies
  refresh_cookie = res.cookies['refreshToken'].value
  access_token = login_data['access_token']
  auth_header = f"Bearer {access_token}"
  print("3. Login: status 201, token access y cookie HttpOnly refreshToken [PASS]")

  # 4. Me
  res = client.get('/api/auth/me', HTTP_AUTHORIZATION=auth_header)
  assert res.status_code == 200, f"Me failed: {res.status_code}"
  me_data = res.json()
  assert me_data['user']['email'] == 'admin@techcorp.com'
  org_id = me_data['user']['organizacion_id']
  print("4. Me: status 200, perfil de usuario autenticado [PASS]")

  # 5. Check Slug
  res = client.get('/api/org/check-slug/techcorp')
  assert res.status_code == 200
  assert res.json()['available'] is False
  assert 'suggestion' in res.json()

  res = client.get('/api/org/check-slug/nueva-empresa-unica')
  assert res.status_code == 200
  assert res.json()['available'] is True
  print("5. Check Slug: disponibilidad y sugerencias [PASS]")

  # 6. Org List & Detail & Update
  res = client.get('/api/org?size=10', HTTP_AUTHORIZATION=auth_header)
  assert res.status_code == 200
  org_list = res.json()
  assert org_list['count'] == 1
  assert org_list['results'][0]['slug'] == 'techcorp'
  assert 'page' in org_list and 'size' in org_list and 'first' in org_list

  res = client.get(f'/api/org/detail/{org_id}', HTTP_AUTHORIZATION=auth_header)
  assert res.status_code == 200
  assert res.json()['name'] == 'TechCorp'

  res = client.patch(f'/api/org/update/{org_id}', {'name': 'TechCorp Global'}, format='json', HTTP_AUTHORIZATION=auth_header)
  assert res.status_code == 200
  assert res.json()['name'] == 'TechCorp Global'
  print("6. Org: Listado con paginación, detalle y actualización [PASS]")

  # 7. Usr List, Create, Soft-delete y Restore
  res = client.get('/api/usr?size=10', HTTP_AUTHORIZATION=auth_header)
  assert res.status_code == 200
  usr_list = res.json()
  assert usr_list['count'] == 5

  # Crear usuario
  new_usr_payload = {
    'email': 'developer@techcorp.com',
    'name': 'Dev TechCorp',
    'password': 'password123',
    'role': 'member',
  }
  res = client.post('/api/usr/create', new_usr_payload, format='json', HTTP_AUTHORIZATION=auth_header)
  assert res.status_code == 201, f"User create failed: {res.status_code} {res.json()}"
  new_user = res.json()
  new_user_id = new_user['id']

  # Soft delete de usuario (DELETE)
  res = client.delete(f'/api/usr/delete/{new_user_id}', HTTP_AUTHORIZATION=auth_header)
  assert res.status_code == 200
  assert 'eliminado correctamente' in res.json()['message']

  # Verificar que no aparece en listado activo
  res = client.get('/api/usr?size=10', HTTP_AUTHORIZATION=auth_header)
  assert not any(u['id'] == new_user_id for u in res.json()['results'])

  # Restore de usuario (PATCH)
  res = client.patch(f'/api/usr/restore/{new_user_id}', HTTP_AUTHORIZATION=auth_header)
  assert res.status_code == 200
  assert 'restaurado correctamente' in res.json()['message']

  # Verificar que reaparece
  res = client.get('/api/usr?size=10', HTTP_AUTHORIZATION=auth_header)
  assert any(u['id'] == new_user_id for u in res.json()['results'])
  print("7. Usr: Listado, creación, soft delete (DELETE) y restore (PATCH) [PASS]")

  # 8. Task List, Create, Filter, Soft-delete y Restore
  res = client.get('/api/task?size=100', HTTP_AUTHORIZATION=auth_header)
  assert res.status_code == 200
  task_list = res.json()
  assert task_list['count'] == 75  # 100 menos 25 eliminadas por defecto en seed

  # Paginación canónica con size=0 (todos los registros envueltos)
  res_all = client.get('/api/task?size=0', HTTP_AUTHORIZATION=auth_header)
  assert res_all.status_code == 200
  task_all = res_all.json()
  assert task_all['count'] == 75
  assert task_all['size'] == 0
  assert task_all['last'] is None
  assert task_all['next'] is None
  assert len(task_all['results']) == 75

  # Paginación estándar (count, page, size, first, last, next, previous, results)
  res = client.get('/api/task?page=1&size=10', HTTP_AUTHORIZATION=auth_header)
  task_page = res.json()
  assert task_page['page'] == 1
  assert task_page['size'] == 10
  assert task_page['first'] == 1
  assert task_page['last'] == 8
  assert task_page['next'] == 2
  assert task_page['previous'] is None

  # Filtrado por fecha exacta (ignorando hora) y rango de fecha
  first_task_date = task_list['results'][0]['created_at'][:10]
  res_date = client.get(f'/api/task?created_at={first_task_date}&size=100', HTTP_AUTHORIZATION=auth_header)
  assert res_date.status_code == 200
  assert res_date.json()['count'] > 0
  assert all(t['created_at'][:10] == first_task_date for t in res_date.json()['results'])

  # Filtrado por rango de fecha pura (_gte y _lte)
  res_range = client.get(f'/api/task?created_at_gte={first_task_date}&created_at_lte={first_task_date}&size=100', HTTP_AUTHORIZATION=auth_header)
  assert res_range.status_code == 200
  assert res_range.json()['count'] == res_date.json()['count']

  # Crear tarea
  new_task_payload = {
    'title': 'Test Task DRF',
    'description': 'Validación de tarea',
    'status': 'yellow',
  }
  res = client.post('/api/task/create', new_task_payload, format='json', HTTP_AUTHORIZATION=auth_header)
  assert res.status_code == 201
  new_task = res.json()
  new_task_id = new_task['id']

  # Actualizar tarea
  res = client.patch(f'/api/task/update/{new_task_id}', {'status': 'green'}, format='json', HTTP_AUTHORIZATION=auth_header)
  assert res.status_code == 200
  assert res.json()['status'] == 'green'

  # Soft delete de tarea (DELETE)
  res = client.delete(f'/api/task/delete/{new_task_id}', HTTP_AUTHORIZATION=auth_header)
  assert res.status_code == 200
  assert 'eliminada correctamente' in res.json()['message']

  # Restore de tarea (PATCH)
  res = client.patch(f'/api/task/restore/{new_task_id}', HTTP_AUTHORIZATION=auth_header)
  assert res.status_code == 200
  assert 'restaurada correctamente' in res.json()['message']
  print("8. Task: Listado con paginación canónica (size=0 y size=10), creación, filtros, soft delete y restore [PASS]")

  # 9. Validación de Conflictos (HTTP 409)
  # Conflicto email duplicado en la misma organización
  dup_usr_payload = {
    'email': 'admin@techcorp.com',
    'name': 'Duplicate Admin',
    'password': 'password123',
    'role': 'member',
  }
  res_dup = client.post('/api/usr/create', dup_usr_payload, format='json', HTTP_AUTHORIZATION=auth_header)
  assert res_dup.status_code == 409, f"Expected 409 on duplicate user email, got {res_dup.status_code}"
  assert 'ya está registrado en esta organización' in res_dup.json()['message']

  # Conflicto slug duplicado en creación de organización
  dup_org_payload = {
    'name': 'TechCorp Duplicate',
    'slug': 'techcorp',
    'user': {
      'email': 'other@dup.com',
      'name': 'Other',
      'password': 'password123',
    }
  }
  res_dup_org = client.post('/api/org/create', dup_org_payload, format='json')
  assert res_dup_org.status_code == 409, f"Expected 409 on duplicate org slug, got {res_dup_org.status_code}"
  assert 'ya está en uso' in res_dup_org.json()['message']
  print("9. Conflictos (HTTP 409): Validación de duplicados en org slug y user email [PASS]")

  # 10. Control de Acceso y Roles (HTTP 403)
  # Login como miembro (no admin)
  member_login = client.post('/api/auth/login', {'email': 'user1@techcorp.com', 'password': '123456'}, format='json')
  assert member_login.status_code == 201
  member_token = member_login.json()['access_token']
  member_header = f"Bearer {member_token}"

  # Miembro intenta crear usuario -> 403 Forbidden
  res_unauth_create = client.post('/api/usr/create', {'email': 'test@techcorp.com', 'name': 'T', 'password': 'pw'}, format='json', HTTP_AUTHORIZATION=member_header)
  assert res_unauth_create.status_code == 403, f"Expected 403 for member user create, got {res_unauth_create.status_code}"

  # Miembro intenta eliminar tarea -> 403 Forbidden
  res_unauth_del_task = client.delete(f'/api/task/delete/{new_task_id}', HTTP_AUTHORIZATION=member_header)
  assert res_unauth_del_task.status_code == 403, f"Expected 403 for member task delete, got {res_unauth_del_task.status_code}"
  print("10. Roles y Permisos: HTTP 403 Forbidden en acciones restringidas a admin [PASS]")

  # 11. Mensajes Canónicos 404
  dummy_uuid = '00000000-0000-0000-0000-000000000000'
  res_404_org = client.get(f'/api/org/detail/{dummy_uuid}', HTTP_AUTHORIZATION=auth_header)
  assert res_404_org.status_code == 404
  assert 'Organización con id "00000000-0000-0000-0000-000000000000" no encontrada' in res_404_org.json()['message']

  res_404_usr = client.get(f'/api/usr/detail/{dummy_uuid}', HTTP_AUTHORIZATION=auth_header)
  assert res_404_usr.status_code == 404
  assert 'Usuario con id "00000000-0000-0000-0000-000000000000" no encontrado' in res_404_usr.json()['message']

  res_404_tsk = client.get(f'/api/task/detail/{dummy_uuid}', HTTP_AUTHORIZATION=auth_header)
  assert res_404_tsk.status_code == 404
  assert 'Tarea con id "00000000-0000-0000-0000-000000000000" no encontrada' in res_404_tsk.json()['message']
  print("11. Mensajes 404 Canónicos: Verificación exacta de cadenas de error [PASS]")

  # 12. Refresh Token
  # Sin cookie
  client.cookies.clear()
  res = client.post('/api/auth/refresh')
  assert res.status_code == 201
  assert res.json()['message'] == 'No refresh token proporcionado'

  # Con cookie
  client.cookies['refreshToken'] = refresh_cookie
  res = client.post('/api/auth/refresh')
  assert res.status_code == 201
  assert 'access_token' in res.json()
  new_access_token = res.json()['access_token']
  assert 'refreshToken' in res.cookies
  print("12. Refresh: rotación de tokens y actualización de cookie [PASS]")

  # 13. Logout & Blacklist
  res = client.post('/api/auth/logout', HTTP_AUTHORIZATION=f"Bearer {new_access_token}")
  assert res.status_code == 201
  assert res.json()['message'] == 'Sesión cerrada exitosamente'
  assert res.cookies['refreshToken']['max-age'] == 0

  # Verificar que el token quedó en lista negra
  res = client.get('/api/auth/me', HTTP_AUTHORIZATION=f"Bearer {new_access_token}")
  assert res.status_code == 401
  assert 'Token invalidado' in res.json()['message']
  print("13. Logout: blacklist de token y borrado de cookie [PASS]")

  # 14. Cleanup Blacklist
  # Iniciar sesión de nuevo para obtener token admin
  res = client.post('/api/auth/login', login_payload, format='json')
  admin_token = res.json()['access_token']
  res = client.post('/api/auth/cleanup-blacklist', HTTP_AUTHORIZATION=f"Bearer {admin_token}")
  assert res.status_code == 201
  assert 'tokens expirados eliminados' in res.json()['message']
  print("14. Cleanup Blacklist: endpoint administrativo [PASS]")

  # 15. Reset canónico (/api/reset)
  res = client.get('/api/reset')
  assert res.status_code == 200
  assert res.json()['totalRemaining'] == 0
  print("15. Reset canónico (/api/reset): tablas vaciadas [PASS]")

  # Restaurar seed final para que la base de datos quede lista para uso
  res = client.get('/api/seed')
  assert res.status_code == 200
  print("16. Seed final restaurado para entorno de desarrollo [PASS]")

  print("\n=== TODAS LAS PRUEBAS PASARON EXITOSAMENTE (100% PASS) ===")

if __name__ == '__main__':
  run_tests()
