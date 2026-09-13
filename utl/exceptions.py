import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException
from django.http import Http404
from django.core.exceptions import PermissionDenied

logger = logging.getLogger(__name__)

class Conflict(APIException):
  status_code = status.HTTP_409_CONFLICT
  default_detail = 'Conflicto con el estado actual del recurso'
  default_code = 'conflict'

def _flatten_errors(detail):
  """Convierte estructuras anidadas de errores de DRF en mensajes planos legibles."""
  if isinstance(detail, list):
    if len(detail) == 1:
      return _flatten_errors(detail[0])
    return [_flatten_errors(item) for item in detail]
  if isinstance(detail, dict):
    messages = []
    for field, errors in detail.items():
      flat = _flatten_errors(errors)
      if isinstance(flat, list):
        for f in flat:
          messages.append(f"{field}: {f}" if field != 'non_field_errors' else str(f))
      else:
        messages.append(f"{field}: {flat}" if field != 'non_field_errors' else str(flat))
    return messages[0] if len(messages) == 1 else messages
  return str(detail)

def custom_exception_handler(exc, context):
  response = exception_handler(exc, context)

  if response is not None:
    status_code = response.status_code
    detail = response.data
    if isinstance(detail, dict):
      if 'detail' in detail:
        msg = _flatten_errors(detail['detail'])
      elif 'message' in detail:
        msg = detail['message']
      else:
        msg = _flatten_errors(detail)
    else:
      msg = _flatten_errors(detail)

    return Response(
      {
        "statusCode": status_code,
        "message": msg,
      },
      status=status_code,
    )

  # Errores no capturados por DRF
  if isinstance(exc, Http404):
    return Response(
      {
        "statusCode": status.HTTP_404_NOT_FOUND,
        "message": str(exc) or "Recurso no encontrado",
      },
      status=status.HTTP_404_NOT_FOUND,
    )

  if isinstance(exc, PermissionDenied):
    return Response(
      {
        "statusCode": status.HTTP_403_FORBIDDEN,
        "message": str(exc) or "Permiso denegado",
      },
      status=status.HTTP_403_FORBIDDEN,
    )

  logger.error("Unhandled Exception: %s", exc, exc_info=True)
  return Response(
    {
      "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
      "message": "Error interno del servidor",
    },
    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
  )
