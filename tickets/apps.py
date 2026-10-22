from django.apps import AppConfig
from django.db.models.signals import post_migrate, post_save


def seed_categories(sender, **kwargs):
    from .models import Category
    for name in ['Hardware', 'Software', 'Network', 'Access & Accounts']:
        Category.objects.get_or_create(name=name)


def create_profile(sender, instance, created, **kwargs):
    from .models import Profile
    if created:
        role = Profile.ADMIN if instance.is_superuser else Profile.EMPLOYEE
        Profile.objects.create(user=instance, role=role)


class TicketsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tickets'

    def ready(self):
        from django.conf import settings
        post_migrate.connect(seed_categories, sender=self)
        post_save.connect(create_profile, sender=settings.AUTH_USER_MODEL)
