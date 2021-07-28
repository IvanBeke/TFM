from typing import Any, Optional
from django.core.management.base import BaseCommand
from django_cassiopeia import cassiopeia as cass
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from web.utils import *
import os, time, shutil, json

class Command(BaseCommand):
    help = 'Import matches from api'
    execution_cache_dir = 'current_execution'
    accounts_state = f'{execution_cache_dir}/accounts.pkl'
    index_state = f'{execution_cache_dir}/accounts_index.pkl'
    delay = 0/100

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        os.makedirs(self.execution_cache_dir, exist_ok=True)
        start = time.time()

        accounts_with_matches = load_execution_state(self.accounts_state, set())

        client = MongoClient()
        db = client.etl
        summoners_collection = db.summoners
        matches_collection = db.matches
        # if len(accounts_with_matches) == 0:
        #     matches_collection.delete_many({})
        summoners = summoners_collection.find({
            'accountId': {
                '$not': {'$in': list(accounts_with_matches)}
            }
        }, {'accountId': 1}, no_cursor_timeout=True).batch_size(50)
        summoners_count = summoners.count() + len(accounts_with_matches)
        for summoner in summoners:
            matches = cass.MatchHistory(
                summoner=cass.Summoner(account_id=summoner['accountId']),
                queues={cass.Queue.ranked_solo_fives},
                end_index=20
            )
            for match in matches:
                match.duration
                match_json = match.to_json()
                match_dict = json.loads(match_json)
                match_dict['gameId'] = match_dict['id']
                del(match_dict['id'])
                try:
                    matches_collection.insert(match_dict)
                except DuplicateKeyError:
                    pass
                time.sleep(self.delay)
            accounts_with_matches.add(summoner['accountId'])
            print(f'Guardaradas {len(matches)} partidas de {len(accounts_with_matches)}/{summoners_count} jugadores')
            save_execution_state(accounts_with_matches, self.accounts_state)


        # Limpiar estados
        shutil.rmtree(self.execution_cache_dir)

        end = time.time()
        print(f'\nEl proceso ha tardado {get_time(end - start)}')