from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from src.models import Customer


class AuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if 'customer_id' in request.session:
            try:
                customer_id = request.session['customer_id']
                customer = Customer.objects.get(id=customer_id)
                request.customer = customer
            except Customer.DoesNotExist:
                request.customer = None
        else:
            request.customer = None
        return None