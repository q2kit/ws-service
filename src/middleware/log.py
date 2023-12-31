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

        logging.info(
            f"IP: {ip} - User: {request.user} - {request.method} - {request.get_full_path()}"
        )

    def process_exception(self, request, exception):
        try:
            LOGGING_EXCEPT_PATHS = settings.LOGGING_EXCEPT_PATHS
        except:
            LOGGING_EXCEPT_PATHS = ()

        if resolve(request.path_info).app_name in LOGGING_EXCEPT_PATHS:
            return None

        ip, _ = get_client_ip(request)

        logging.error(
            " - ".join(
                (
                    f"IP: {ip}",
                    f"User: {request.user}",
                    f"{request.method}",
                    f"{request.get_full_path()}",
                    f"{exception}",
                )
            )
        )
