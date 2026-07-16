"""WSGI config for the OpenShop project."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "openshop.settings")

application = get_wsgi_application()
