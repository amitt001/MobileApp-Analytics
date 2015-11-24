from django.conf import settings

API_URL = getattr(settings, 'API_URL', 'http://0.0.0.0:5000')
