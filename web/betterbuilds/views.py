from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django_cassiopeia import cassiopeia as cass
from .models import FrequentBuilds

def index(request: HttpRequest) -> HttpResponse:
    return render(request, 'betterbuilds/index.html', {})

def champions(request: HttpRequest) -> HttpResponse:
    champion_list = cass.Champions(included_data={'image', 'id', 'name'}, locale='es_ES')
    return render(request, 'betterbuilds/champions.html', {
        'champions': champion_list,
    })

def champions_builds(request: HttpRequest, champion_id: int) -> HttpResponse:
    champion = cass.Champion(id=champion_id, locale='es_ES')
    frequent_build = FrequentBuilds.objects.filter(champion=champion_id, type='basic').first()
    items = {}
    if frequent_build is not None:
        for build in frequent_build.builds:
            build['support'] = round(build['support'], 2) * 100
            build['items'] = list()
            for item in build['itemsets']:
                build['items'].append(cass.Item(id=item))
            build['items'] = sorted(build['items'], key=lambda item:-item.gold.total)
    return render(request, 'betterbuilds/champion_builds.html', {
        'champion': champion,
        'frequent_build': frequent_build,
        'items': items,
    })
