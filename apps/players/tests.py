import os
import shutil
import string
import random
from datetime import date

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms import widgets
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from apps.auth.models import UserProfile

from apps.clubs.models import Club
from apps.more.models import Regulation
from apps.players.forms import PlayerForm, PlayerSearchForm
from .models import Player, PlayerStats

class PlayerModelTest(TestCase):
    def setUp(self):
        self.club = Club.objects.create(name='Test Club')
        self.player = Player.objects.create(
            name='John Doe',
            dob=date(1990, 1, 1),
            height=175,
            weight=70,
            club=self.club,
            nationality='English',
            position='MF',
            # image=image,
            type='HG'
        )

    def test_creating_player(self):
        self.assertTrue(isinstance(self.player, Player))
        self.assertEqual(self.player.__str__(), self.player.name)

    def test_updating_player(self):
        new_name = 'Jane Doe'
        self.player.name = new_name
        self.player.save()
        self.assertEqual(self.player.name, new_name)

        new_dob = date(1980, 10, 10)
        self.player.dob = new_dob
        self.player.save()
        self.assertEqual(self.player.dob, new_dob)

        new_height = 180
        self.player.height = new_height
        self.player.save()
        self.assertEqual(self.player.height, new_height)

        new_weight = 80
        self.player.weight = new_weight
        self.player.save()
        self.assertEqual(self.player.weight, new_weight)

        new_club = Club.objects.create(name='New Test Club')
        self.player.club = new_club
        self.player.save()
        self.assertEqual(self.player.club, new_club)

        new_nationality = 'Spanish'
        self.player.nationality = new_nationality
        self.player.save()
        self.assertEqual(self.player.nationality, new_nationality)

        new_position = 'FW'
        self.player.position = new_position
        self.player.save()
        self.assertEqual(self.player.position, new_position)

        new_type = 'FR'
        self.player.type = new_type
        self.player.save()
        self.assertEqual(self.player.type, new_type)

    def test_deleting_player(self):
        self.assertIsNotNone(self.player.id)
        self.player.delete()
        self.assertEqual(Player.objects.count(), 0)
        with self.assertRaises(Player.DoesNotExist):
            Player.objects.get(id=self.player.id)

class PlayerStatsModelTest(TestCase):
    def setUp(self):
        self.club = Club.objects.create(name='Test Club')
        self.player = Player.objects.create(
            name='John Doe',
            dob=date(1990, 1, 1),
            height=175,
            weight=70,
            club=self.club,
            nationality='English',
            position='MF',
            # image=image,
            type='HG'
        )

    def test_accessing_player_stats(self):
        self.assertIsInstance(self.player.player_stats, PlayerStats)

    def test_player_stats_default_values(self):
        self.assertEqual(self.player.player_stats.goals, 0)
        self.assertEqual(self.player.player_stats.assists, 0)
        self.assertEqual(self.player.player_stats.appearances, 0)

    def test_updating_player_stats(self):
        goals = 2
        self.player.player_stats.goals = goals
        self.player.save()
        self.assertEqual(self.player.player_stats.goals, goals)

        assists = 1
        self.player.player_stats.assists = assists
        self.player.save()
        self.assertEqual(self.player.player_stats.assists, assists)

        appearances = 5
        self.player.player_stats.appearances = appearances
        self.player.save()
        self.assertEqual(self.player.player_stats.appearances, appearances)

def generate_random_string(length):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))

class PlayerFormTest(TestCase):
    def setUp(self):
        self.club = Club.objects.create(name='Test Club')
        Regulation.objects.get_or_create(pk=1)

    def test_initial_values(self):
        form = PlayerForm()
        self.assertEqual(form.fields['dob'].initial, date.today())
        self.assertIsInstance(form.fields['dob'].widget, widgets.DateInput)

    def test_valid_data(self):
        form = PlayerForm(data={
            'name': 'John Doe',
            'dob': date(1990, 1, 1),
            'height': 180,
            'weight': 80,
            'club': self.club.id,
            'nationality': 'English',
            'position': 'FW',
            'type': 'HR'
        })
        self.assertTrue(form.is_valid())

    """
    Test player name field
    """
    def test_name_with_special_characters(self):
        form = PlayerForm(data={
            'name': '123&*(!@#!@)',
            'dob': date(1990, 1, 1),
            'height': 180,
            'weight': 80,
            'club': self.club.id,
            'nationality': 'English',
            'position': 'FW',
            'type': 'HR'
        })
        self.assertFalse(form.is_valid())

    def test_name_empty(self):
        form = PlayerForm(data={
            'name': '',
            'dob': date(1990, 1, 1),
            'height': 180,
            'weight': 80,
            'club': self.club.id,
            'nationality': 'English',
            'position': 'FW',
            'type': 'HR'
        })
        self.assertFalse(form.is_valid())

    def test_name_valid_boundary(self):
        form = PlayerForm(data={
            'name': generate_random_string(255),
            'dob': date(1990, 1, 1),
            'height': 180,
            'weight': 80,
            'club': self.club.id,
            'nationality': 'English',
            'position': 'FW',
            'type': 'HR'
        })
        self.assertTrue(form.is_valid())

    def test_name_invalid_boudary(self):
        form = PlayerForm(data={
            'name': generate_random_string(256),
            'dob': date(1990, 1, 1),
            'height': 180,
            'weight': 80,
            'club': self.club.id,
            'nationality': 'English',
            'position': 'FW',
            'type': 'HR'
        })
        self.assertFalse(form.is_valid())

    """
    Test dob field
    """
    def test_dob_empty(self):
        form = PlayerForm(data={
            'name': 'John Doe',
            'dob': '',
            'height': 180,
            'weight': 80,
            'club': self.club.id,
            'nationality': 'English',
            'position': 'FW',
            'type': 'HR'
        })
        self.assertFalse(form.is_valid())

    def test_dob_valid_boundary(self):
        form1 = PlayerForm(data={
            'name': 'John Doe',
            'dob': date(date.today().year - Regulation.objects.get(pk=1).player_min_age, date.today().month, date.today().day),
            'height': 180,
            'weight': 80,
            'club': self.club.id,
            'nationality': 'English',
            'position': 'FW',
            'type': 'HR'
        })
        self.assertTrue(form1.is_valid())

        form2 = PlayerForm(data={
            'name': 'John Doe',
            'dob': date(date.today().year - Regulation.objects.get(pk=1).player_max_age, date.today().month, date.today().day),
            'height': 180,
            'weight': 80,
            'club': self.club.id,
            'nationality': 'English',
            'position': 'FW',
            'type': 'HR'
        })
        self.assertTrue(form2.is_valid())

    def test_dob_invalid_boundary(self):
        form1 = PlayerForm(data={
            'name': 'John Doe',
            'dob': date(date.today().year - Regulation.objects.get(pk=1).player_min_age + 1, date.today().month, date.today().day),
            'height': 180,
            'weight': 80,
            'club': self.club.id,
            'nationality': 'English',
            'position': 'FW',
            'type': 'HR'
        })
        self.assertFalse(form1.is_valid())

        form2 = PlayerForm(data={
            'name': 'John Doe',
            'dob': date(date.today().year - Regulation.objects.get(pk=1).player_max_age - 1, date.today().month, date.today().day),
            'height': 180,
            'weight': 80,
            'club': self.club.id,
            'nationality': 'English',
            'position': 'FW',
            'type': 'HR'
        })
        self.assertFalse(form2.is_valid())

    """
    Test height field
    """
    def test_empty_height(self):
        form = PlayerForm(data={
            'name': 'John Doe',
            'dob': date(1990, 1, 1),
            'height': '',
            'weight': 80,
            'club': self.club.id,
            'nationality': 'English',
            'position': 'FW',
            'type': 'HR'
        })
        self.assertFalse(form.is_valid())

    def test_negative_height(self):
        form = PlayerForm(data={
            'name': 'John Doe',
            'dob': date(1990, 1, 1),
            'height': -180,
            'weight': 80,
            'club': self.club.id,
            'nationality': 'English',
            'position': 'FW',
            'type': 'HR'
        })
        self.assertFalse(form.is_valid())

    """
    Test weight field
    """
    def test_empty_weight(self):
        form = PlayerForm(data={
            'name': 'John Doe',
            'dob': date(1990, 1, 1),
            'height': 180,
            'weight': '',
            'club': self.club.id,
            'nationality': 'English',
            'position': 'FW',
            'type': 'HR'
        })
        self.assertFalse(form.is_valid())

    def test_negative_weight(self):
        form = PlayerForm(data={
            'name': 'John Doe',
            'dob': date(1990, 1, 1),
            'height': 180,
            'weight': -80,
            'club': self.club.id,
            'nationality': 'English',
            'position': 'FW',
            'type': 'HR'
        })
        self.assertFalse(form.is_valid())

    """
    Test club field
    """
    def test_empty_club(self):
        form = PlayerForm(data={
            'name': 'John Doe',
            'dob': date(1990, 1, 1),
            'height': 180,
            'weight': 80,
            'club': '',
            'nationality': 'English',
            'position': 'FW',
            'type': 'HR'
        })
        self.assertFalse(form.is_valid())

    """
    Test nationality field
    """
    def test_empty_nationality(self):
        form = PlayerForm(data={
            'name': 'John Doe',
            'dob': date(1990, 1, 1),
            'height': 180,
            'weight': 80,
            'club': self.club.id,
            'nationality': '',
            'position': 'FW',
            'type': 'HR'
        })
        self.assertFalse(form.is_valid())

    """
    Test position field
    """
    def test_empty_position(self):
        form = PlayerForm(data={
            'name': 'John Doe',
            'dob': date(1990, 1, 1),
            'height': 180,
            'weight': 80,
            'club': self.club.id,
            'nationality': 'English',
            'position': '',
            'type': 'HR'
        })
        self.assertFalse(form.is_valid())

class PlayerViewTest(TestCase):
    @override_settings(MEDIA_ROOT=os.path.join('tmp'))
    def setUp(self):
        os.makedirs('tmp', exist_ok=True)

        self.client = Client()

        self.admin = User.objects.create_user(username='admin', password='admin123')
        UserProfile.objects.create(user=self.admin, type='admin')

        with open('test_media/test_club_logo.png', 'rb') as logo_file:
            logo = SimpleUploadedFile(logo_file.name,
                                      logo_file.read(),
                                      content_type='image/png')
            self.club = Club.objects.create(name='Test Club', logo=logo)

        with open('test_media/test_player.png', 'rb') as image_file:
            image = SimpleUploadedFile(image_file.name,
                                       image_file.read(),
                                       content_type='image/png')
            self.player1 = Player.objects.create(
                name='John Doe',
                dob=date(1990, 1, 1),
                height=175,
                weight=70,
                club=self.club,
                nationality='English',
                position='MF',
                image=image,
                type='HG'
            )
            self.player2 = Player.objects.create(
                name='Jack Doe',
                dob=date(1990, 1, 1),
                height=175,
                weight=70,
                club=self.club,
                nationality='English',
                position='MF',
                image=image,
                type='HG'
            )

        self.client.login(username='admin', password='admin123')

    @override_settings(MEDIA_ROOT=os.path.join('tmp'))
    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT)

    @override_settings(MEDIA_ROOT=os.path.join('tmp'))
    def test_index_view(self):
        with open('test_media/test_player.png', 'rb') as image_file:
            image = SimpleUploadedFile(image_file.name,
                                       image_file.read(),
                                       content_type='image/png')
            player1 = Player.objects.create(
                name='John Doe 1',
                dob=date(1990, 1, 1),
                height=175,
                weight=70,
                club=self.club,
                nationality='English',
                position='MF',
                image=image,
                type='HG'
            )
            player2 = Player.objects.create(
                name='John Doe 2',
                dob=date(1990, 1, 1),
                height=175,
                weight=70,
                club=self.club,
                nationality='English',
                position='MF',
                image=image,
                type='HG'
            )
            player3 = Player.objects.create(
                name='John Doe 3',
                dob=date(1990, 1, 1),
                height=175,
                weight=70,
                club=self.club,
                nationality='English',
                position='MF',
                image=image,
                type='HG'
            )
            player4 = Player.objects.create(
                name='John Doe 4',
                dob=date(1990, 1, 1),
                height=175,
                weight=70,
                club=self.club,
                nationality='English',
                position='MF',
                image=image,
                type='HG'
            )

        url = reverse('players:index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'players/index.html')
        self.assertContains(response, self.player1.name)
        self.assertContains(response, self.player2.name)
        self.assertContains(response, player1.name)
        self.assertContains(response, player2.name)
        self.assertContains(response, player3.name)
        self.assertContains(response, player4.name)

        self.assertIn('user', response.context)
        self.assertEqual(response.context['user'], self.admin)

        self.assertIn('clubs', response.context)
        self.assertEqual(len(response.context['clubs']), 1)

        self.assertIn('highlight_players', response.context)
        self.assertEqual(len(response.context['highlight_players']), 4)
        self.assertEqual(response.context['highlight_players'][2].name, 'John Doe 1')

        self.assertIsInstance(response.context['form'], PlayerSearchForm)

    @override_settings(MEDIA_ROOT=os.path.join('tmp'))
    def test_add_view(self):
        url = reverse('players:add')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        with open('test_media/test_player.png', 'rb') as image_file:
            image = SimpleUploadedFile(image_file.name,
                                       image_file.read(),
                                       content_type='image/png')

            data = {
                'name': 'New Player',
                'dob': date(1990, 1, 1),
                'height': 175,
                'weight': 70,
                'club': self.club.id,
                'nationality': 'English',
                'position': 'FW',
                'image': image,
                'type': 'HG'
            }

            response = self.client.post(url, data, follow=True)
            self.assertEqual(response.status_code, 302)
            self.assertTemplateUsed(response, 'players/add.html')
            self.assertTrue(Player.objects.filter(name='New Player').exists())

            self.assertIn('user', response.context)
            self.assertEqual(response.context['user'], self.admin)

            self.assertIsInstance(response.context['form'], PlayerForm)

            self.assertIn('submitted', response.context)
            self.assertTrue(response.context['submitted'])

            self.assertIn('clubs', response.context)
            self.assertEqual(len(response.context['clubs']), 1)

    def test_detail_view(self):
        url = reverse('players:view', args=[self.player1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'players/view.html')

        self.assertIn('user', response.context)
        self.assertEqual(response.context['user'], self.admin)

        self.assertIn('clubs', response.context)
        self.assertEqual(len(response.context['clubs']), 1)

        self.assertIn('player', response.context)
        self.assertEqual(response.context['player'].name, 'John Doe')

    @override_settings(MEDIA_ROOT=os.path.join('tmp'))
    def test_edit_view(self):
        url = reverse('players:edit', args=[self.player1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'players/add.html')

        with open('test_media/test_player.png', 'rb') as image_file:
            image = SimpleUploadedFile(image_file.name,
                                       image_file.read(),
                                       content_type='image/png')

            data = {
                'name': 'Something Doe',
                'dob': self.player1.dob,
                'height': self.player1.height,
                'weight': self.player1.weight,
                'club': self.club.id,
                'nationality': self.player1.nationality,
                'position': self.player1.position,
                'image': image,
                'type': self.player1.type
            }

            response = self.client.post(url, data, follow=True)
            self.assertEqual(response.status_code, 302)
            self.player1.refresh_from_db()
            self.assertEqual(self.player1.name, 'Something Doe')

            self.assertIn('user', response.context)
            self.assertEqual(response.context['user'], self.admin)

            self.assertIsInstance(response.context['form'], PlayerForm)

            self.assertIn('clubs', response.context)
            self.assertEqual(len(response.context['clubs']), 1)

    def test_delete_view(self):
        url = reverse('players:delete', args=[self.player1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Player.objects.filter(id=self.player1.id).exists())

    def test_search_view(self):
        url = reverse('players:search')
        response = self.client.get(url, {'player_name': 'John Doe'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'players/search.html')
        
        self.assertIn('found_players', response.context)
        self.assertIn(self.player1, response.context['found_players'])
        self.assertNotIn(self.player2, response.context['found_players'])

        self.assertIn('user', response.context)
        self.assertEqual(response.context['user'], self.admin)

        self.assertIsInstance(response.context['form'], PlayerSearchForm)

        self.assertIn('clubs', response.context)
        self.assertEqual(len(response.context['clubs']), 1)
