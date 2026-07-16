"""ASGI config for the OpenShop project."""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "openshop.settings")

application = get_asgi_application()
