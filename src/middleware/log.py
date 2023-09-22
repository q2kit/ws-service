from django.utils.deprecation import MiddlewareMixin
from django.conf import settings 
from django.urls import resolve

import logging
from ipware import get_client_ip


class RequestLoggerMiddleware(MiddlewareMixin):
    def process_request(self, request):
        try:
            LOGGING_EXCEPT_PATHS = settings.LOGGING_EXCEPT_PATHS
        except:
            LOGGING_EXCEPT_PATHS = ()

        if resolve(request.path_info).app_name in LOGGING_EXCEPT_PATHS:
            return None
        
        ip, _ = get_client_ip(request)
        customer_id = request.customer.pk if request.customer else 'Anonymous'

        logging.info(f"IP: {ip} - CustomerID: {customer_id} - {request.method} - {request.path}")

    def process_exception(self, request, exception):
        try:
            LOGGING_EXCEPT_PATHS = settings.LOGGING_EXCEPT_PATHS
        except:
            LOGGING_EXCEPT_PATHS = ()

        if resolve(request.path_info).app_name in LOGGING_EXCEPT_PATHS:
            return None
        
        ip, _ = get_client_ip(request)
        customer_id = request.customer.pk if request.customer else 'Anonymous'

        logging.error(f"IP: {ip} - CustomerID: {customer_id} - {request.method} - {request.path} - {exception}")
