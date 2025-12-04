from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"

class MaterialsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "materials"

    def ready(self):
        # Регистрируем сигнал
        import materials.signals  # noqa: F401
