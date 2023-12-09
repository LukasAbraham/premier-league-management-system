from django.db import models
from apps.clubs.models import Club
from .choices import NATIONALITY_CHOICES, POSITION_CHOICES, TYPE_CHOICES
from datetime import date

class Player(models.Model):
    name = models.CharField(max_length=255)
    dob = models.DateField()
    height = models.FloatField()
    weight = models.FloatField()
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    nationality = models.CharField(max_length=30, choices=NATIONALITY_CHOICES)
    position = models.CharField(max_length=3, choices=POSITION_CHOICES)
    image = models.ImageField(upload_to='player_imgs/', blank=True)
    type = models.CharField(max_length=2, choices=TYPE_CHOICES, default='HG')
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        self.club.update_status()
        if is_new:
            PlayerStats.objects.create(player=self)
    
    @property
    def age(self):
        today = date.today()
        return today.year - self.dob.year - ((self.dob.month, self.dob.day) > (today.month, today.day)) 
    
class PlayerStats(models.Model):
    player = models.OneToOneField(Player, on_delete=models.CASCADE, related_name='player_stats')
    goals = models.PositiveIntegerField(default=0)
    assists = models.PositiveIntegerField(default=0)
    appearances = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.player.name} - {self.appearances} - {self.goals} goals, {self.assists} assists'
