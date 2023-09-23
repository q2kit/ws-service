from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from src.models import Project

import jwt


def create_example_token(request, secret_key):
    return HttpResponse(
        jwt.encode(
            {
                "client_id": "123",
            },
            secret_key,
            algorithm="HS256",
        )
    )


@csrf_exempt
def refresh_secret_key(request, project_id):
    if request.method != "POST":
        return HttpResponse("NG", status=400)
    try:
        if request.user.is_superuser:
            Project.objects.get(name=project_id).refresh_secret_key()
        else:
            Project.objects.get(name=project_id, owner=request.user).refresh_secret_key()
        messages.success(request, "Secret key refreshed successfully")
        return HttpResponse("OK")
    except:
        return HttpResponse("NG", status=400)
