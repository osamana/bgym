from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CoreConfig(AppConfig):
    name = "gym_management_system.core"
    verbose_name = _("Gym Manager")

    def ready(self):
        try:
            import gym_management_system.core.signals  # noqa: F401
        except ImportError:
            pass
