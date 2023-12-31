from django.db import models
from django.templatetags.static import static
from apps.managers.models import Manager
from apps.more.models import Regulation
from .choices import STADIUM_CHOICES, SPONSOR_CHOICES, STATUS_CHOICES, CITY_CHOICES, CUP_CHOICES, CUP_CHOICES_DICT

class Club(models.Model):
    name = models.CharField(max_length=255, unique=True)
    logo = models.ImageField(upload_to='club_imgs/')
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='I')
    stadium = models.CharField(max_length=2, choices=STADIUM_CHOICES)
    sponsor = models.CharField(max_length=2, choices=SPONSOR_CHOICES, blank=True)
    established_year = models.PositiveIntegerField(null=True, blank=True)
    location = models.CharField(max_length=2, choices=CITY_CHOICES, default='', blank=True)
    website = models.URLField(max_length=255, null=True, blank=True)
    owner = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            ClubStats.objects.create(club=self)
    
    def update_status(self):
        if Regulation.objects.exists():
            regulation = Regulation.objects.get(pk=1)
            max_foreign_players = regulation.max_foreign_players
            max_players = regulation.max_players
            min_players = regulation.min_players        
            
            foreign_players = self.player_set.filter(nationality='English').count()
            total_players = self.player_set.count()
            try: 
                manager = Manager.objects.get(club=self)
            except Manager.DoesNotExist:
                manager = None
            
            if foreign_players <= max_foreign_players and total_players <= max_players and total_players >= min_players and manager is not None:
                self.status = 'V'
            else:
                self.status = 'I'
                
            self.save()
        
    
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
    
class Achievement(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    cup = models.CharField(max_length=3, choices=CUP_CHOICES)
    year = models.PositiveIntegerField()
    image = models.CharField(max_length=255, blank=True)
    
    def __str__(self):
        return f'{self.club.name} won {self.cup} in {self.year}'

    def save(self, *args, **kwargs):
        if self.cup:
            self.image = CUP_CHOICES_DICT[self.cup][1]
        super().save(*args, **kwargs)
        
    def get_img_url(self):
        return static('cup_imgs/' + self.image)
