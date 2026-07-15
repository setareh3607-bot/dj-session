import json

from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser
from django.http import JsonResponse

from .models import Session


def test_session_view(request):
    session_key = getattr(request, "session_key", None)
    raw_data = getattr(request, "session_data", "")

    try:
        data = json.loads(raw_data) if raw_data else {}
    except json.JSONDecodeError:
        data = {}

    if not session_key:
        return JsonResponse(
            {
                "error": "No session key found.",
                "session_key": None,
                "session_data": data,
            },
            status=400,
        )

    try:
        session = Session.objects.get(session_key=session_key)
    except Session.DoesNotExist:
        return JsonResponse(
            {
                "error": "Session not found in database.",
                "session_key": session_key,
                "session_data": data,
            },
            status=404,
        )

    new_name = request.GET.get("name")
    if new_name:
        data["name"] = new_name
        session.session_data = json.dumps(data)
        session.save(update_fields=["session_data"])
        request.session_data = session.session_data
        request.session_user_id = session.user_id

    return JsonResponse(
        {
            "session_key": session_key,
            "session_data": data,
            "user_id": getattr(request, "session_user_id", None),
        }
    )


def login_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method is allowed."}, status=405)

    username = request.POST.get("username")
    password = request.POST.get("password")

    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({"error": "Invalid credentials"}, status=400)

    session_key = getattr(request, "session_key", None)
    if not session_key:
        return JsonResponse({"error": "No active session found."}, status=400)

    Session.objects.filter(session_key=session_key).update(user_id=user.id)

    if hasattr(request, "custom_session"):
        request.custom_session.user_id = user.id
    request.session_user_id = user.id
    request.user = user

    return JsonResponse(
        {
            "message": "Login successful",
            "user_id": user.id,
        }
    )


def logout_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method is allowed."}, status=405)

    session_key = getattr(request, "session_key", None)
    if session_key:
        Session.objects.filter(session_key=session_key).update(user_id=None)

    if hasattr(request, "custom_session"):
        request.custom_session.user_id = None
    request.session_user_id = None
    request.user = AnonymousUser()

    return JsonResponse({"message": "Logout successful"})
