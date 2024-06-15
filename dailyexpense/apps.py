from django.apps import AppConfig


class DailyexpenseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dailyexpense'

    def ready(self):
        import dailyexpense.signals
