from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django_cassiopeia import cassiopeia as cass


def index(request: HttpRequest) -> HttpResponse:
    return render(request, 'betterbuilds/index.html', {})

def champions(request: HttpRequest) -> HttpResponse:
    champion_list = cass.get_champions()
    return render(request, 'betterbuilds/champions.html', {
        'champions': champion_list,
    })
