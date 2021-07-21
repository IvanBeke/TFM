from typing import Any, Optional
from django.core.management.base import BaseCommand
from pymongo import MongoClient
from web.utils import *
import time

class Command(BaseCommand):
    help = 'Generate transactions from matches'

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        start = time.time()

        client = MongoClient()
        client.etl.matches.aggregate([
            {
                '$unwind': {
                    'path': '$participants'
                }
            }, {
                '$set': {
                    'items': [
                        '$participants.stats.item0',
                        '$participants.stats.item1',
                        '$participants.stats.item2',
                        '$participants.stats.item3',
                        '$participants.stats.item4',
                        '$participants.stats.item5',
                        '$participants.stats.item6'
                    ]
                }
            }, {
                '$group': {
                    '_id': '$participants.championId',
                    'championId': {
                        '$first': '$participants.championId'
                    },
                    'transactions': {
                        '$push': '$items'
                    }
                }
            }, {
                '$out': 'transactions'
            }
        ])

        end = time.time()
        print(f'\nEl proceso ha tardado {get_time(end - start)}')