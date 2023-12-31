# Generated by Django 4.2.7 on 2023-11-29 13:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0002_alter_club_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='club',
            name='established_year',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='club',
            name='location',
            field=models.CharField(choices=[('BA', 'Bath'), ('BI', 'Birmingham'), ('BR', 'Bradford'), ('BH', 'Brighton and Hove'), ('BU', 'Bristol'), ('CA', 'Cambridge'), ('CN', 'Canterbury'), ('CR', 'Carlisle'), ('CM', 'Chelmsford'), ('CH', 'Chester'), ('CI', 'Chichester'), ('CO', 'Colchester'), ('CV', 'Coventry'), ('DE', 'Derby'), ('DO', 'Doncaster'), ('DU', 'Durham'), ('EL', 'Ely'), ('EX', 'Exeter'), ('GL', 'Gloucester'), ('HE', 'Hereford'), ('HU', 'Kingston upon Hull'), ('LA', 'Lancaster'), ('LE', 'Leeds'), ('LI', 'Leicester'), ('LC', 'Lichfield'), ('LN', 'Lincoln'), ('LV', 'Liverpool'), ('LO', 'London'), ('MA', 'Manchester'), ('MK', 'Milton Keynes'), ('NE', 'Newcastle upon Tyne'), ('NO', 'Norwich'), ('NG', 'Nottingham'), ('OX', 'Oxford'), ('PE', 'Peterborough'), ('PL', 'Plymouth'), ('PO', 'Portsmouth'), ('PR', 'Preston'), ('RI', 'Ripon'), ('SA', 'Salford'), ('SB', 'Salisbury'), ('SH', 'Sheffield'), ('SO', 'Southampton'), ('SE', 'Southend-on-Sea'), ('ST', 'St Albans'), ('SN', 'Stoke-on-Trent'), ('SU', 'Sunderland'), ('TR', 'Truro'), ('WA', 'Wakefield'), ('WE', 'Wells'), ('WS', 'Westminster'), ('WI', 'Winchester'), ('WO', 'Wolverhampton'), ('WR', 'Worcester'), ('YO', 'York')], default='LO', max_length=2),
        ),
        migrations.AddField(
            model_name='club',
            name='owner',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='club',
            name='website',
            field=models.URLField(blank=True, max_length=255, null=True),
        ),
        migrations.CreateModel(
            name='Achievement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cup', models.CharField(choices=[('EPL', 'Premier League'), ('CBC', 'Carabao Cup'), ('FA', 'FA Cup'), ('EFL', 'EFL Cup'), ('CS', 'Community Shield'), ('UEL', 'UEFA Europa League'), ('UCL', 'UEFA Champions League')], max_length=3)),
                ('year', models.PositiveIntegerField()),
                ('image', models.CharField(blank=True, max_length=255)),
                ('club', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clubs.club')),
            ],
        ),
    ]
