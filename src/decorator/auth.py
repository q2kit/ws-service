from django.shortcuts import redirect


def login_required(func):
    def wrapper(request, *args, **kwargs):
        if request.customer:
            return func(request, *args, **kwargs)
        else:
            return redirect("signin")

    return wrapper
