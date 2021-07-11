from django.shortcuts import render
from django.http import HttpRequest, HttpResponse


def index(request: HttpRequest) -> HttpResponse:
    return render(request, 'betterbuilds/index.html', {})

def champions(request: HttpRequest) -> HttpResponse:
    pass
