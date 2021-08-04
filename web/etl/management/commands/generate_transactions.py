from typing import Any, Optional
from django.core.management.base import BaseCommand
from pymongo import MongoClient
from web.utils import *
from django_cassiopeia import cassiopeia as cass
import time

class Command(BaseCommand):
    help = 'Generate transactions from matches'

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        start = time.time()
        items = cass.Items()
        exclude_items = [0]
        for item in items:
            if 'Boots' in item.tags or len(item.builds_from) == 0:
                exclude_items.append(item.id)

        client = MongoClient()
        client.etl.matches.aggregate([
            {
                '$unwind': {
                    'path': '$teams'
                }
            },
            {
                '$unwind': {
                    'path': '$teams.participants'
                }
            },
            {
                '$set': {
                    'items': [
                        '$teams.participants.stats.item0',
                        '$teams.participants.stats.item1',
                        '$teams.participants.stats.item2',
                        '$teams.participants.stats.item3',
                        '$teams.participants.stats.item4',
                        '$teams.participants.stats.item5'
                    ]
                }
            },
            {
                '$project': {
                    'teams.participants.championId': 1,
                    'teams.participants.position': 1,
                    'items': {
                        '$filter': {
                            'input': '$items',
                            'as': 'item',
                            'cond': {
                                '$not': {
                                    '$in': ['$$item', exclude_items]
                                }
                            }
                        }
                    }
                }
            },
            {
                '$group': {
                    '_id': {
                        'champ': '$teams.participants.championId',
                        'pos': '$teams.participants.position'
                    },
                    'championId': {
                        '$first': '$teams.participants.championId'
                    },
                    'position': {
                        '$first': '$teams.participants.position'
                    },
                    'transactions': {
                        '$push': '$items'
                    }
                }
            },
            {
                '$out': 'transactions'
            }
        ], allowDiskUse=True)

        end = time.time()
        print(f'\nEl proceso ha tardado {get_time(end - start)}')