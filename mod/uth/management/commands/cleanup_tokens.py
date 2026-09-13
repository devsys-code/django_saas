from django.core.management.base import BaseCommand
from mod.uth.services import clean_expired_blacklist, clean_expired_refresh_tokens

class Command(BaseCommand):
  help = 'Limpia tokens expirados de la blacklist y refresh tokens revocados/expirados'

  def handle(self, *args, **options):
    bl_count = clean_expired_blacklist()
    rt_count = clean_expired_refresh_tokens()
    self.stdout.write(
      self.style.SUCCESS(
        f'Limpieza completada: {bl_count} tokens de blacklist y {rt_count} refresh tokens eliminados.'
      )
    )
