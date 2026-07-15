import json
import secrets
from datetime import timedelta

from django.utils import timezone

from .models import Session


class SimpleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def _create_session(self):
        expire_date = timezone.now() + timedelta(days=1)
        return Session.objects.create(
            session_key=secrets.token_hex(32),
            user_id=None,
            session_data=json.dumps({}),
            expire_date=expire_date,
        )

    def __call__(self, request):
        session_key = request.COOKIES.get("sessionid")
        session = None

        if session_key:
            try:
                session = Session.objects.get(session_key=session_key)

                if session.expire_date < timezone.now():
                    session.delete()
                    session = self._create_session()
                else:
                    session.expire_date = timezone.now() + timedelta(days=1)
                    session.save(update_fields=["expire_date"])
            except Session.DoesNotExist:
                session = self._create_session()
        else:
            session = self._create_session()

        request.session_key = session.session_key
        request.session_data = session.session_data

        response = self.get_response(request)
        response.set_cookie(
            "sessionid",
            session.session_key,
            expires=session.expire_date,
            httponly=True,
        )
        return response
