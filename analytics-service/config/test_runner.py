from django.test.runner import DiscoverRunner


class UnmanagedModelTestRunner(DiscoverRunner):
    """Test runner that creates tables for unmanaged models (managed=False)."""

    def setup_databases(self, **kwargs):
        result = super().setup_databases(**kwargs)

        from django.apps import apps
        from django.db import connection

        with connection.schema_editor() as schema_editor:
            for model in apps.get_models():
                if not model._meta.managed:
                    try:
                        schema_editor.create_model(model)
                    except Exception:
                        pass  # Table might already exist

        return result
