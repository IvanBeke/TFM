from typing import Any, Optional
from django_cassiopeia import cassiopeia as cass
from django.core.management.base import BaseCommand
from pymongo import MongoClient
import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpmax, fpgrowth, apriori
from web.utils import *
from betterbuilds.models import FrequentBuilds
import time

class Command(BaseCommand):
    help = 'Generate frequent builds based on transactions'
    min_support = 0.1

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        start = time.time()

        client = MongoClient()
        transactions = client.etl.transactions.find({})
        FrequentBuilds.objects.all().delete()
        for champion_builds in transactions:
            te = TransactionEncoder()
            encoded_builds = te.fit_transform(champion_builds['transactions'])
            df = pd.DataFrame(encoded_builds, columns=te.columns_)
            result = apriori(df, min_support=self.min_support, use_colnames=True).to_dict(orient='records')
            frequent_build = FrequentBuilds()
            frequent_build.champion = champion_builds['championId']
            frequent_build.games = len(champion_builds['transactions'])
            builds = []
            for itemset in result:
                items = []
                for item in itemset['itemsets']:
                    items.append(cass.Item(id=item, locale='es_ES'))
                items.sort(key=lambda item:-item.gold.total)
                items = list(map(lambda item: item.id, items))
                builds.append({
                    'support': itemset['support'],
                    'itemset': items
                })
            frequent_build.builds = builds
            frequent_build.save()

        end = time.time()
        print(f'\nEl proceso ha tardado {get_time(end - start)}')