from django.shortcuts import redirect, render
from django.contrib import messages
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
    frequent_builds = FrequentBuilds.objects.filter(champion=champion_id).all()
    total_games = 0
    if frequent_builds is not None:
        for frequent_build in frequent_builds:
            total_games += frequent_build.games
            for build in frequent_build.builds:
                build['support'] = round(build['support'] * 100, 2)
                build['items'] = list()
                for item in build['itemset']:
                    build['items'].append(cass.Item(id=item, locale='es_ES', version='11.15.1'))
    return render(request, 'betterbuilds/champion_builds.html', {
        'champion': champion,
        'frequent_builds': frequent_builds,
        'total_games': total_games,
    })

def champion_for_current_match(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        summoner_name = request.POST.get('summoner-name')
        summoner = cass.Summoner(name=summoner_name)
        if not summoner.exists:
            messages.error(request, f'No existen jugadores con el nombre {summoner_name}', 'alert-danger')
        else:
            current_match = summoner.current_match
            if current_match.exists:
                for player in current_match.participants:
                    if player.summoner.name == summoner.name:
                        champion = player.champion
                        messages.success(request, 'Partida encontrada correctamente', 'alert-success')
                        return redirect(champions_builds, champion_id=champion.id)
                messages.error(request, f'El jugador {summoner.name} no se encuentra en la partida buscada', 'alert-danger')
            else:
                messages.error(request, f'El jugador {summoner.name} no está actualmente en una partida', 'alert-danger')
    else:
        messages.error(request, 'Búsqueda realizada con un método no permitido', 'alert-danger')
    return redirect(champions)