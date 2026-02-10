"""
Local development settings - uses SQLite so you can run without MySQL.
Usage: python manage.py runserver --settings=ludmilportifolio.settings_local
"""
from .settings import *  # noqa: F401, F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
