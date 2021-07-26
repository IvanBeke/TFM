from djongo import models

class FrequentBuilds(models.Model):
    champion = models.IntegerField()
    games = models.IntegerField()
    builds = models.JSONField()

    class Meta:
        db_table = 'frequent_builds'
