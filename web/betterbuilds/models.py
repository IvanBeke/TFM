from djongo import models
from enum import Enum

class FrequentBuilds(models.Model):
    champion = models.IntegerField()
    games = models.IntegerField()
    position = models.CharField(max_length=25)
    builds = models.JSONField()

    class Meta:
        db_table = 'frequent_builds'

    def position_name(self):
        positions = Positions.get_positions_dict()
        return positions[self.position]

    def position_percentage(self, total_games: int) -> float:
        return round(self.games / total_games * 100, 2)

class Positions(Enum):
    TOP = ('TOP', 'Top')
    JUNGLE = ('JUNGLE', 'Jungla')
    MIDDLE = ('MIDDLE', 'Mid')
    BOTTOM = ('BOTTOM', 'Bot')
    UTILITY = ('UTILITY', 'Apoyo')
    UNKNOWN = ('UNKNOWN', 'Desconocido')

    def __init__(self, position, display_name) -> None:
        self.position = position
        self.display_name = display_name

    @classmethod
    def get_positions_dict(cls):
        return {k: v.display_name for k, v in cls.__members__.items()}