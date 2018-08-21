from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

MASTER_API_TOKEN = getattr(settings, 'LINKSAVE_MASTER_API_TOKEN', None)
if MASTER_API_TOKEN is None:
    raise ImproperlyConfigured("You must configure a master API token")
