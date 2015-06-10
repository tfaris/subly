import os

from django.conf import settings


SUBLY_CLIENT_ID = getattr(settings, 'SUBLY_CLIENT_ID', os.environ['SUBLY_CLIENT_ID'])
SUBLY_CLIENT_SECRET = getattr(settings, 'SUBLY_CLIENT_SECRET', os.environ['SUBLY_CLIENT_SECRET'])
