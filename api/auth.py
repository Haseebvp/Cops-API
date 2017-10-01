import base64
import binascii
from rest_framework.authentication import (
    BaseAuthentication
)
from rest_framework import exceptions
from rest_framework.authentication import get_authorization_header
from django.core.exceptions import ObjectDoesNotExist
from api.models import Device, Session


class DemoTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.META.get("HTTP_TOKEN", "")
        if not token:
            msg = ('Invalid token header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        try:
            token = token.decode()
        except UnicodeError:
            msg = (
                'Invalid token header.'
                ' Token string should not contain invalid characters.'
            )
            raise exceptions.AuthenticationFailed(msg)
        try:
            session = Session.objects.select_related('device').get(token=token)
        except ObjectDoesNotExist:
            msg = ('Invalid token header. Token doesn\'t exist')
            raise exceptions.AuthenticationFailed(msg)
        return (session.device, None)