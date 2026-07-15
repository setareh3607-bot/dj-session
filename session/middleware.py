import json
import secrets
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
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

        request.custom_session = session
        request.session_key = session.session_key
        request.session_data = session.session_data
        request.session_user_id = session.user_id

        response = self.get_response(request)
        response.set_cookie("sessionid", session.session_key, expires=session.expire_date, httponly=True)
        return response

class CustomAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.user_model = get_user_model()

    def __call__(self, request):
        request.user = AnonymousUser()
        user_id = getattr(request, "session_user_id", None)
        if user_id:
            try:
                request.user = self.user_model.objects.get(id=user_id)
            except self.user_model.DoesNotExist:
                pass
        return self.get_response(request)
