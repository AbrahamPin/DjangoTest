"""
WSGI config for YAAS project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from django.core.management import call_command
call_command('runcrons')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "YAAS.settings")

application = get_wsgi_application()
