from django.db import models
from utl.models import SoftDeleteModel

class Organizacion(SoftDeleteModel):
  name = models.CharField(max_length=255)
  slug = models.CharField(max_length=100, unique=True)

  class Meta:
    db_table = 'Organizacion'
    ordering = ['-created_at']

  def __str__(self):
    return self.name
