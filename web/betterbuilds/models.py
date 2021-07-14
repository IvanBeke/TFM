from djongo import models

class FrequentBuilds(models.Model):
    champion = models.IntegerField()
    type = models.CharField(max_length=25)
    builds = models.JSONField()

    class Meta:
        db_table = 'frequent_builds'
