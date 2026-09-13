import uuid
from django.db import models
from django.utils import timezone

class RefreshToken(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  jti = models.CharField(max_length=255, unique=True)
  user_id = models.CharField(max_length=255)
  expires_at = models.DateTimeField(db_index=True)
  replaced_by = models.CharField(max_length=255, null=True, blank=True)
  revoked = models.BooleanField(default=False)
  created_at = models.DateTimeField(default=timezone.now)

  class Meta:
    db_table = 'RefreshToken'
    indexes = [
      models.Index(fields=['expires_at'], name='idx_refreshtoken_expires_at'),
    ]

  def __str__(self):
    return f"RefreshToken({self.jti}, revoked={self.revoked})"

class TokenBlacklist(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  jti = models.CharField(max_length=255, unique=True)
  user_id = models.CharField(max_length=255)
  expired_at = models.DateTimeField()
  created_at = models.DateTimeField(default=timezone.now)

  class Meta:
    db_table = 'TokenBlacklist'

  def __str__(self):
    return f"TokenBlacklist({self.jti})"
