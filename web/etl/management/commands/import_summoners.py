from typing import Any, Optional
from django.core.management.base import BaseCommand
from django_cassiopeia import cassiopeia as cass
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from web.utils import *
import os, copy, time, shutil

class Command(BaseCommand):
    help = 'Import summoners from api'
    PIPELINE = [
        {
            'method': cass.get_challenger_league,
            'name': 'CHALLENGER',
            'completed': False,
            'params': {
                'queue': cass.Queue.ranked_solo_fives,
            }
        },
        {
            'method': cass.get_grandmaster_league,
            'name': 'GRANDMASTER',
            'completed': False,
            'params': {
                'queue': cass.Queue.ranked_solo_fives,
            }

        },
        {
            'method': cass.get_master_league,
            'name': 'MASTER',
            'completed': False,
            'params': {
                'queue': cass.Queue.ranked_solo_fives,
            }
        },
        {
            'method': cass.get_paginated_league_entries,
            'name': f'{cass.Tier.diamond} {cass.Division.one}',
            'completed': False,
            'params': {
                'queue': cass.Queue.ranked_solo_fives,
                'tier': cass.Tier.diamond,
                'division': cass.Division.one,
            }
        },
    ]
    execution_cache_dir = 'current_execution'
    leagues_state_file = f'{execution_cache_dir}/remaining_leagues.pkl'
    players_file = f'{execution_cache_dir}/players.pkl'
    accounts_file = f'{execution_cache_dir}/accounts.pkl'
    summoners_index = f'{execution_cache_dir}/summoners_index.pkl'
    delay = 60/100

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        os.makedirs(self.execution_cache_dir, exist_ok=True)
        start = time.time()
        # Leer un fichero del estado de la ejecución si existe o copiar PIPELINE
        # para empezar desde 0
        leagues_current_execution = load_execution_state(self.leagues_state_file, copy.deepcopy(self.PIPELINE))
        players = load_execution_state(self.players_file, [])
        # Filtrar las fases que ya estén completas
        leagues_current_execution = list(filter(lambda league: not league['completed'], leagues_current_execution))
        for league in leagues_current_execution:
            entries = league['method'](**league['params'])
            if hasattr(entries, 'entries'):
                entries = entries.entries
            players.extend(entries)
            print(f'{league["name"]}: len: {len(entries)} / total: {len(players)}')
            league['completed'] = True
            save_execution_state(leagues_current_execution, self.leagues_state_file)
            save_execution_state(players, self.players_file)
            time.sleep(self.delay)

        accounts = load_execution_state(self.accounts_file, [])
        summoners_index = load_execution_state(self.summoners_index, 0)

        client = MongoClient()
        db = client.etl
        collection = db.summoners
        # if summoners_index == 0:
        #     collection.delete_many({})
        for player in players[summoners_index:]:
            summoner = player.summoner
            summoner.account_id  # Forzar a pedir los datos
            summoner_dict = summoner.to_dict()
            summoner_dict['summonerId'] = summoner_dict['id']
            del(summoner_dict['id'])
            try:
                collection.insert(summoner_dict)
            except DuplicateKeyError:
                pass
            summoners_index += 1
            print(f'{summoners_index}/{len(players)} jugadores guardados')
            save_execution_state(accounts, self.accounts_file)
            save_execution_state(summoners_index, self.summoners_index)
            time.sleep(self.delay)

        # Limpiar estados
        shutil.rmtree(self.execution_cache_dir)

        end = time.time()
        print(f'\nEl proceso ha tardado {get_time(end - start)}')