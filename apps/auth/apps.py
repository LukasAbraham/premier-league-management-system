from django.apps import AppConfig


class AuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.auth'
    # this attribute allows relabeling an application when 2 applications have conflicting labels.
    # It defaults to the last component of name
    label = 'user_auth'
