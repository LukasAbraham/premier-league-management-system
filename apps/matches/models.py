from django.db import models
from django.utils import timezone
from apps.clubs.models import Club
from apps.players.models import Player
from apps.clubs.choices import STADIUM_CHOICES

class Match(models.Model):
    STATUS_CHOICES = [
        ('P', 'Previous'),
        ('U', 'Upcoming'),
    ]
    
    round = models.PositiveSmallIntegerField()
    time = models.DateTimeField()
    club1 = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='club1')
    club2 = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='club2')
    stadium = models.CharField(max_length=2, choices=STADIUM_CHOICES)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)

    def __str__(self):
        return f'Round: {self.round} {self.club1.name} vs {self.club2.name}'
    
    def save(self, *args, **kwargs):
        if self.time < timezone.now():
            self.status = 'P'
        else: 
            self.status = 'U'
            
        self.stadium = self.club1.stadium
        super().save(*args, **kwargs)
        
    def delete(self, *args, **kwargs):
        if hasattr(self, 'result'):
            self.result.delete()
        for goal_event in self.goal_event.all():
            goal_event.delete()
        super().delete(*args, **kwargs)
    
class Result(models.Model):
    club1_goals = models.PositiveIntegerField()
    club2_goals = models.PositiveIntegerField()
    match = models.OneToOneField(Match, on_delete=models.CASCADE, related_name='result', null=True)
    
    def __str__(self):
        return f"Result: {self.match.club1.name} {self.club1_goals} - {self.club2_goals} {self.match.club2.name}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        club1_stats = self.match.club1.club_stats
        club2_stats = self.match.club2.club_stats
        if self.club1_goals > self.club2_goals:
            club1_stats.wins += 1
            club2_stats.losses += 1
        elif self.club1_goals < self.club2_goals:
            club1_stats.losses += 1
            club2_stats.wins += 1
        else:
            club1_stats.draws += 1
            club2_stats.draws += 1
        club1_stats.save()
        club2_stats.save()

    def update(self, old_result):
        # Get the ClubStats instances for the clubs
        club1_stats = self.match.club1.club_stats
        club2_stats = self.match.club2.club_stats

        # Rollback the stats of the clubs to their state before the result was edited
        if old_result.club1_goals > old_result.club2_goals:
            club1_stats.wins -= 1
            club2_stats.losses -= 1
        elif old_result.club1_goals < old_result.club2_goals:
            club1_stats.losses -= 1
            club2_stats.wins -= 1
        else:
            club1_stats.draws -= 1
            club2_stats.draws -= 1

        # Update the stats of the clubs based on the current state of the result
        if self.club1_goals > self.club2_goals:
            club1_stats.wins += 1
            club2_stats.losses += 1
        elif self.club1_goals < self.club2_goals:
            club1_stats.losses += 1
            club2_stats.wins += 1
        else:
            club1_stats.draws += 1
            club2_stats.draws += 1

        # Save the updated ClubStats instances
        club1_stats.save()
        club2_stats.save()

    def delete(self, *args, **kwargs):
        club1_stats = self.match.club1.club_stats
        club2_stats = self.match.club2.club_stats
        if self.club1_goals > self.club2_goals:
            club1_stats.wins -= 1
            club2_stats.losses -= 1
        elif self.club1_goals < self.club2_goals:
            club1_stats.losses -= 1
            club2_stats.wins -= 1
        else:
            club1_stats.draws -= 1
            club2_stats.draws -= 1
        club1_stats.save()
        club2_stats.save()
        super().delete(*args, **kwargs)

class GoalEvent(models.Model):
    TYPE_CHOICES = [
        ('N', 'Normal'),
        ('FK', 'Free kick'),
        ('OG', 'Own goal'),
    ]
    
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="goal_event", null=True)
    scoring_player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='scoring_event')
    assisting_player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='assisting_event', null=True, blank=True)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    type = models.CharField(max_length=3, choices=TYPE_CHOICES, default='N')
    time = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"{self.scoring_player.name} scored a {self.get_type_display()} at {self.time}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.type != 'OG':
            # update the stats of the player who scored
            scoring_player_stats = self.scoring_player.player_stats
            scoring_player_stats.goals += 1
            scoring_player_stats.save()
            # update the stats of the player who assisted
            if self.assisting_player is not None:
                assisting_player_stats = self.assisting_player.player_stats
                assisting_player_stats.assists += 1
                assisting_player_stats.save()
        
        
    def update(self, old_goal_event):
        # Rollback the stats of the players to their state before the goal event was edited
        if old_goal_event.type != 'OG':
            old_scoring_player_stats = old_goal_event.scoring_player.player_stats
            old_scoring_player_stats.goals -= 1
            old_scoring_player_stats.save()
            if old_goal_event.assisting_player is not None:
                old_assisting_player_stats = old_goal_event.assisting_player.player_stats
                old_assisting_player_stats.assists -= 1
                old_assisting_player_stats.save()

        # Update the stats of the players based on the current state of the goal event
        if self.type != 'OG':
            scoring_player_stats = self.scoring_player.player_stats
            scoring_player_stats.goals += 1
            scoring_player_stats.save()
            if self.assisting_player is not None:
                assisting_player_stats = self.assisting_player.player_stats
                assisting_player_stats.assists += 1
                assisting_player_stats.save()

        
    def delete(self, *args, **kwargs):
        if self.type != 'OG':
            # rollback the stats of the scoring player to previous state
            scoring_player_stats = self.scoring_player.player_stats
            scoring_player_stats.goals -= 1
            scoring_player_stats.save()
            if self.assisting_player is not None:
                # rollback the stats of the assisting player to previous state
                assisting_player_stats = self.assisting_player.player_stats
                assisting_player_stats.assists -= 1
                assisting_player_stats.save()
        super().delete(*args, **kwargs)
