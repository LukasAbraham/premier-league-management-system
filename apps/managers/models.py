from django.db import models
from apps.players.choices import NATIONALITY_CHOICES
from datetime import date

class Manager(models.Model):
    name = models.CharField(max_length=255)
    nationality = models.CharField(max_length=30, choices=NATIONALITY_CHOICES)
    dob = models.DateField()
    club = models.OneToOneField('clubs.Club', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='manager_imgs/', blank=True)
    
    def __str__(self):
        return self.name
    
    @property
    def age(self):
        today = date.today()
        return today.year - self.dob.year - ((self.dob.month, self.dob.day) > (today.month, today.day))