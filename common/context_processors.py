from django.http import HttpRequest
from django.conf import settings

def project_settings(request: HttpRequest):
    return {'settings': settings}
