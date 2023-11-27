from django.db import models
from apps.managers.models import Manager
from apps.more.models import Regulation
from .choices import STADIUM_CHOICES, SPONSOR_CHOICES

class Club(models.Model):
    STATUS_CHOICES = [
        ('V', 'Valid'),
        ('I', 'Invalid'),
    ]

    name = models.CharField(max_length=255, unique=True)
    logo = models.ImageField(upload_to='club_imgs/')
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='I')
    stadium = models.CharField(max_length=2, choices=STADIUM_CHOICES)
    sponsor = models.CharField(max_length=2, choices=SPONSOR_CHOICES, blank=True)
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            ClubStats.objects.create(club=self)
    
    def update_status(self, max_foreign_players, min_players, max_players):
        foreign_players = self.player_set.filter(nationality='England').count()
        total_players = self.player_set.count()
        try: 
            manager = Manager.objects.get(club=self)
        except Manager.DoesNotExist:
            manager = None
        
        if foreign_players <= max_foreign_players and total_players <= max_players and total_players >= min_players and manager is not None:
            self.status = 'V'
        else:
            self.status = 'I'
        
    
class ClubStats(models.Model):
    club = models.OneToOneField(Club, on_delete=models.CASCADE, related_name='club_stats')
    goals = models.PositiveIntegerField(default=0)
    conceded_goals = models.PositiveIntegerField(default=0)
    wins = models.PositiveIntegerField(default=0)
    losses = models.PositiveIntegerField(default=0)
    draws = models.PositiveIntegerField(default=0)
    
    @property
    def goal_difference(self):
        return self.goals - self.conceded_goals
    
    @property
    def points(self):
        regulation = Regulation.objects.get(pk=1)
        return regulation.win_points * self.wins + regulation.draw_points * self.draws + regulation.loss_points * self.losses
    