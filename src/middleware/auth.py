from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from src.models import Customer


class AuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        try:
            request.customer = Customer.objects.get(id=request.session["customer_id"])
        except:
            request.customer = None
