from django.db import models

class Regulation(models.Model):
    min_age = models.PositiveIntegerField(default=16)
    max_age = models.PositiveIntegerField(default=40)
    min_players = models.PositiveIntegerField(default=15)
    max_players = models.PositiveIntegerField(default=40)
    max_foreign_players = models.PositiveIntegerField(default=10)
    win_points = models.IntegerField(default=3)
    loss_points = models.IntegerField(default=0)
    draw_points = models.IntegerField(default=1)
    duration = models.IntegerField(default=90)