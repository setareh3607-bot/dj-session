from .models import Session


class SimpleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        
        cookies = request.COOKIES.get("sessionid")
        if cookies:
            try:
                session = Session.objects.get(session_key=cookies)
                print(session_data)
            except Session.DoesNotExist:
                print("Session not found")
        response = self.get_response(request)
        return response