# Generated by Django 4.1.7 on 2023-11-30 04:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0004_alter_club_location'),
    ]

    operations = [
        migrations.AlterField(
            model_name='achievement',
            name='cup',
            field=models.CharField(choices=[('EPL', 'Premier League'), ('FA', 'FA Cup'), ('EFL', 'EFL Cup'), ('CS', 'Community Shield'), ('UEL', 'UEFA Europa League'), ('UCL', 'UEFA Champions League')], max_length=3),
        ),
    ]
