from django.db import models
from utl.models import TenantModel

class Task(TenantModel):
  STATUS_CHOICES = [
    ('red', 'Red'),
    ('yellow', 'Yellow'),
    ('green', 'Green'),
  ]

  title = models.CharField(max_length=255)
  description = models.TextField(null=True, blank=True)
  status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='red')

  class Meta:
    db_table = 'Task'
    ordering = ['-created_at']

  def __str__(self):
    return self.title
