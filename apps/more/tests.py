from datetime import date
import os
import shutil

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from apps.auth.models import UserProfile
from apps.clubs.models import Club, ClubStats
from apps.players.models import Player, PlayerStats

from .models import Regulation
from .forms import RegulationForm

class RegulationFormTest(TestCase):
    def test_valid_data(self):
        form = RegulationForm({
            'player_min_age': 16,
            'player_max_age': 40,
            'manager_min_age': 30,
            'manager_max_age': 80,
            'min_players': 15,
            'max_players': 40,
            'max_foreign_players': 10,
            'win_points': 4,
            'loss_points': 0,
            'draw_points': 2,
            'duration': 90,
        })
        print(form.errors)
        self.assertTrue(form.is_valid())

    def test_field_validation(self):
        form = RegulationForm({
            'player_min_age': -1,  # Invalid value
            'player_max_age': 40,
            'manager_min_age': 30,
            'manager_max_age': 80,
            'min_players': 15,
            'max_players': 40,
            'max_foreign_players': 10,
            'win_points': 4,
            'loss_points': 0,
            'draw_points': 2,
            'duration': 'abc'  # Invalid type
        })
        self.assertFalse(form.is_valid())

    def test_win_points_validation(self):
        form = RegulationForm({
            'player_min_age': 16,
            'player_max_age': 40,
            'manager_min_age': 30,
            'manager_max_age': 80,
            'min_players': 15,
            'max_players': 40,
            'max_foreign_players': 10,
            'win_points': 1,
            'loss_points': 2,
            'draw_points': 2,
            'duration': 90,
        })
        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error('win_points'))

    def test_loss_points_validation(self):
        form = RegulationForm({
            'player_min_age': 16,
            'player_max_age': 40,
            'manager_min_age': 30,
            'manager_max_age': 80,
            'min_players': 15,
            'max_players': 40,
            'max_foreign_players': 10,
            'win_points': 1,
            'loss_points': 2,
            'draw_points': 1,
            'duration': 90,
        })
        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error('loss_points'))

    def test_draw_points_validation(self):
        form = RegulationForm({
            'player_min_age': 16,
            'player_max_age': 40,
            'manager_min_age': 30,
            'manager_max_age': 80,
            'min_players': 15,
            'max_players': 40,
            'max_foreign_players': 10,
            'win_points': 1,
            'loss_points': 1,
            'draw_points': 2,
            'duration': 90,
        })
        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error('draw_points'))

class RegulationViewTest(TestCase):
    @override_settings(MEDIA_ROOT=os.path.join('tmp'))
    def create_test_club(self, name):
        with open('test_media/test_club_logo.png', 'rb') as logo_file:
            logo = SimpleUploadedFile(logo_file.name,
                                      logo_file.read(),
                                      content_type='image/png')
        return Club.objects.create(
            name=name,
            logo=logo
        )

    @override_settings(MEDIA_ROOT=os.path.join('tmp'))
    def create_test_player(self, name, club):
        with open('test_media/test_player.png', 'rb') as image_file:
            image = SimpleUploadedFile(image_file.name,
                                       image_file.read(),
                                       content_type='image/png')
        return Player.objects.create(
            name=name,
            dob=date(1990, 10, 10),
            height=180,
            weight=80,
            club=club,
            nationality='English',
            position='FW',
            image=image,
        )

    @override_settings(MEDIA_ROOT=os.path.join('tmp'))
    def setUp(self):
        os.makedirs('tmp', exist_ok=True)

        self.client = Client()

        self.admin = User.objects.create(username='admin', password='admin123')
        UserProfile.objects.create(user=self.admin, type='admin')

        self.client.login(username='admin', password='admin123')

    @override_settings(MEDIA_ROOT=os.path.join('tmp'))
    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT)

    def test_index_view(self):
        clubs = [self.create_test_club(f"Test Club {i}") for i in range(4)]
        url = reverse('more:index')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'more/index.html')

        self.assertIn('clubs', response.context)
        self.assertEqual(len(response.context['clubs']), len(clubs))

    def test_view_regulation_view(self):
        url = reverse('more:view_regulation')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn('regulation', response.context)
        self.assertIsInstance(response.context['regulation'], Regulation)

    def test_edit_regulation_view(self):
        url = reverse('more:edit_regulation')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'more/edit_regulation.html')

        data = {
            'player_min_age': 16,
            'player_max_age': 40,
            'manager_min_age': 30,
            'manager_max_age': 80,
            'min_players': 15,
            'max_players': 40,
            'max_foreign_players': 10,
            'win_points': 4,
            'loss_points': 0,
            'draw_points': 2,
            'duration': 90,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)

    def test_standing_view(self):
        club1 = self.create_test_club('Club 1')
        club1.club_stats.goals = 3
        club1.club_stats.wins = 3
        club1.club_stats.losses = 1
        club1.save()

        club2 = self.create_test_club('Club 2')
        club2.club_stats.goals = 1
        club2.club_stats.wins = 1
        club2.club_stats.losses = 3
        club2.save()

        url = reverse('more:standing')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'more/standing.html')
        self.assertIn('clubs', response.context)
        self.assertEqual(len(response.context['clubs']), 2)
        self.assertIn('standings', response.context)
        self.assertEqual(len(response.context['standings']), 2)

    def test_stats_records_view(self):
        club = self.create_test_club('Test Club')

        player1 = self.create_test_player('Player 1', club)
        player2 = self.create_test_player('Player 2', club)

        url = reverse('more:stats_records') 
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'more/stats_records.html')
        self.assertIn('top_scorers', response.context)
        self.assertEqual(len(response.context['top_scorers']), 2)
        self.assertIn('top_play_makers', response.context)
        self.assertEqual(len(response.context['top_play_makers']), 2)

    def test_report_view(self):
        pass

    def test_export_to_pdf(self):
        pass
