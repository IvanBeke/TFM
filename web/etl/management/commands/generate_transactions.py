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
                    'path': '$participants'
                }
            },
            {
                '$set': {
                    'items': [
                        '$participants.stats.item0',
                        '$participants.stats.item1',
                        '$participants.stats.item2',
                        '$participants.stats.item3',
                        '$participants.stats.item4',
                        '$participants.stats.item5'
                    ]
                }
            },
            {
                '$project': {
                    'participants.championId': 1,
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
                    '_id': '$participants.championId',
                    'championId': {
                        '$first': '$participants.championId'
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