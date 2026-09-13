from django.utils import timezone
from rest_framework import generics, status, exceptions
from rest_framework.response import Response

class BaseSoftDeleteView(generics.UpdateAPIView):
  """
  Vista genérica para Soft Delete heredando de UpdateAPIView (sin DestroyAPIView).
  Mapea la petición DELETE a una mutación de estado lógico usando perform_update.
  """
  entity_name = "Recurso"
  gender = "m"  # 'm' o 'f'
  lookup_field = 'id'

  def get_object(self):
    lookup_val = self.kwargs.get(self.lookup_field)
    term = "no encontrada" if self.gender == 'f' else "no encontrado"
    try:
      obj = self.get_queryset().get(**{self.lookup_field: lookup_val})
      self.check_object_permissions(self.request, obj)
      return obj
    except Exception:
      raise exceptions.NotFound(f'{self.entity_name} con id "{lookup_val}" {term}')

  def perform_update(self, serializer):
    serializer.instance.deleted_at = timezone.now()
    serializer.instance.is_active = False
    serializer.save()

  def delete(self, request, *args, **kwargs):
    instance = self.get_object()
    if instance.deleted_at is not None:
      term = "no encontrada" if self.gender == 'f' else "no encontrado"
      raise exceptions.NotFound(f'{self.entity_name} con id "{instance.id}" {term}')

    serializer = self.get_serializer(instance, data={}, partial=True)
    serializer.is_valid(raise_exception=True)
    self.perform_update(serializer)

    term_elim = "eliminada" if self.gender == 'f' else "eliminado"
    return Response(
      {"message": f"{self.entity_name} {term_elim} correctamente"},
      status=status.HTTP_200_OK,
    )

  def patch(self, request, *args, **kwargs):
    return self.delete(request, *args, **kwargs)

class BaseRestoreView(generics.UpdateAPIView):
  """
  Vista genérica para Restore heredando de UpdateAPIView (sin DestroyAPIView).
  Mapea la petición PATCH a una restauración de estado lógico usando perform_update.
  """
  entity_name = "Recurso"
  gender = "m"  # 'm' o 'f'
  lookup_field = 'id'

  def get_queryset(self):
    return super().get_queryset().all()

  def get_object(self):
    lookup_val = self.kwargs.get(self.lookup_field)
    term = "no encontrada o no eliminada" if self.gender == 'f' else "no encontrado o no eliminado"
    try:
      obj = self.get_queryset().get(**{self.lookup_field: lookup_val})
      self.check_object_permissions(self.request, obj)
      return obj
    except Exception:
      raise exceptions.NotFound(f'{self.entity_name} con id "{lookup_val}" {term}')

  def perform_update(self, serializer):
    serializer.instance.deleted_at = None
    serializer.instance.is_active = True
    serializer.save()

  def patch(self, request, *args, **kwargs):
    instance = self.get_object()
    if instance.deleted_at is None:
      term = "no encontrada o no eliminada" if self.gender == 'f' else "no encontrado o no eliminado"
      raise exceptions.NotFound(f'{self.entity_name} con id "{instance.id}" {term}')

    serializer = self.get_serializer(instance, data={}, partial=True)
    serializer.is_valid(raise_exception=True)
    self.perform_update(serializer)

    term_rest = "restaurada" if self.gender == 'f' else "restaurado"
    return Response(
      {"message": f"{self.entity_name} {term_rest} correctamente"},
      status=status.HTTP_200_OK,
    )
