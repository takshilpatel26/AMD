from django.apps import AppConfig


class MetersConfig(AppConfig):
    name = 'meters'

    def ready(self):
        import meters.signals
