from django.shortcuts import redirect
from django.http import JsonResponse


def customer_login_required(func):
    def wrapper(request, *args, **kwargs):
        if request.customer:
            return func(request, *args, **kwargs)
        else:
            return redirect("signin")

    return wrapper


def user_login_required(func):
    def wrapper(request, *args, **kwargs):
        if request.user:
            return func(request, *args, **kwargs)
        else:
            return JsonResponse({"error": "Unauthorized"}, status=401)

    return wrapper
