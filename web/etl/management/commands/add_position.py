from typing import Any, List, Optional
from roleidentification import pull_data, get_roles
from django.core.management.base import BaseCommand
from pymongo import MongoClient
from web.utils import *
import time

class Command(BaseCommand):
    help = 'Add position attribute to matches'

    def __get_position(self, participant: dict) -> str:
        lane = participant['timeline']['lane']
        role = participant['timeline']['role']
        if lane in {'JUNGLE', 'TOP', 'MIDDLE'}:
            return lane
        elif role == 'DUO_CARRY':
            return 'BOTTOM'
        elif role == 'DUO_SUPPORT':
            return 'UTILITY'

    def __get_positions(self, participants: List[dict]) -> dict:
        positions = {
            'TOP': 0,
            'JUNGLE': 0,
            'MIDDLE': 0,
            'BOTTOM': 0,
            'UTILITY': 0,
        }
        for participant in participants:
            position = self.__get_position(participant)
            positions[position] = participant['championId']
        return positions

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        start = time.time()

        data = pull_data()
        client = MongoClient()
        matches = client.etl.matches.find({}, no_cursor_timeout=True).batch_size(2000)
        matches_count = matches.count()
        updated = 0
        for match in matches:
            for team in match['teams']:
                champions = []
                for participant in team['participants']:
                    champions.append(participant['championId'])
                try:
                    roles = get_roles(data, champions)
                except KeyError:
                    roles = self.__get_positions(team['participants'])
                roles = {v: k for k, v in roles.items()}
                for participant in team['participants']:
                    participant['position'] = roles.get(participant['championId'], 'UNKNOWN')
            client.etl.matches.replace_one({'_id': match['_id']}, match)
            updated += 1
            print(f'Posiciones añadidas en {updated}/{matches_count} totales')

        end = time.time()
        print(f'\nEl proceso ha tardado {get_time(end - start)}')