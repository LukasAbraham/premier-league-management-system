import os
import shutil
from datetime import date
import string
import random

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from apps.auth.models import UserProfile
from apps.clubs.choices import CUP_CHOICES_DICT
from apps.clubs.views import update_clubs_status
from .models import Club, ClubStats, Achievement
from .forms import ClubForm, ClubSearchForm, AchievementForm
from apps.more.models import Regulation

class ClubModelTest(TestCase):
    def setUp(self):
        os.makedirs('tmp', exist_ok=True)
        
        self.regulation = Regulation.objects.get_or_create(pk=1)

        self.club = self.create_test_club('Test Club')

    @override_settings(MEDIA_ROOT=os.path.join('tmp'))
    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT)

    @override_settings(MEDIA_ROOT=os.path.join('tmp'))
    def create_test_club(self, name):
        with open('test_media/test_club_logo.png', 'rb') as logo_file:
            logo = SimpleUploadedFile(logo_file.name,
                                      logo_file.read(),
                                      content_type='image/png')
            return Club.objects.create(
                name=name,
                logo=logo,
                stadium='AN',
            )

    def test_creating_club(self):
        club = self.create_test_club('New Club')

        self.assertTrue(isinstance(club, Club))
        self.assertEqual(club.__str__(), club.name)

    def test_creating_club_with_same_name(self):
        with self.assertRaises(IntegrityError):
            Club.objects.create(name='Test Club')

    def test_updating_club(self):
        new_name = 'New Club'
        self.club.name = new_name
        self.club.save()
        self.assertEqual(self.club.name, new_name)

        new_stadium = 'Etihad Stadium'
        self.club.stadium = new_stadium
        self.club.save()
        self.assertEqual(self.club.stadium, new_stadium)

    def test_deleting_club(self):
        self.assertIsNotNone(self.club.id)
        self.club.delete()
        self.assertEqual(Club.objects.count(), 0)
        with self.assertRaises(Club.DoesNotExist):
            Club.objects.get(id=self.club.id)

class ClubStatsModelTest(TestCase):
    def setUp(self):
        os.makedirs('tmp', exist_ok=True)

        self.club = self.create_test_club('Test Club')

    @override_settings(MEDIA_ROOT=os.path.join('tmp'))
    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT)

    @override_settings(MEDIA_ROOT=os.path.join('tmp'))
    def create_test_club(self, name):
        with open('test_media/test_club_logo.png', 'rb') as logo_file:
            logo = SimpleUploadedFile(logo_file.name,
                                      logo_file.read(),
                                      content_type='image/png')
            return Club.objects.create(
                name=name,
                logo=logo,
                stadium='AN',
            )

    def test_club_stats_access_through_club(self):
        self.assertTrue(isinstance(self.club.club_stats, ClubStats))
        self.assertEqual(self.club.club_stats.club, self.club)
        self.assertEqual(self.club.club_stats.goals, 0)
        self.assertEqual(self.club.club_stats.conceded_goals, 0)
        self.assertEqual(self.club.club_stats.wins, 0)
        self.assertEqual(self.club.club_stats.losses, 0)
        self.assertEqual(self.club.club_stats.draws, 0)

    def test_goal_difference_property(self):
        self.club.club_stats.goals = 5
        self.club.club_stats.conceded_goals = 2
        self.club.save()

        self.assertTrue(self.club.club_stats.goal_difference, 3)

    def test_updating_club_stats(self):
        self.club.club_stats.goals = 3
        self.club.club_stats.wins = 2
        self.club.club_stats.draws = 1
        self.club.save()

        self.assertEqual(self.club.club_stats.goals, 3)
        self.assertEqual(self.club.club_stats.wins, 2)
        self.assertEqual(self.club.club_stats.draws, 1)

    def test_points_calculation(self):
        self.club.club_stats.wins = 2
        self.club.club_stats.draws = 1
        self.club.save()

        self.assertEqual(self.club.club_stats.points, 7)

class AchievementModelTest(TestCase):
    def setUp(self):
        # Create a Club for testing
        self.club = Club.objects.create(name='Test Club')

    def test_save_method_sets_image(self):
        # Test that the image field is set correctly based on cup choice
        achievement = Achievement.objects.create(
            club=self.club,
            cup='EPL',
            year=2023
        )
        expected_image = CUP_CHOICES_DICT['EPL'][1]
        self.assertEqual(achievement.image, expected_image)

    def test_save_method_without_cup(self):
        # Test that the image field remains empty when cup is not provided
        achievement = Achievement.objects.create(
            club=self.club,
            year=2023
        )
        self.assertEqual(achievement.image, '')

    def test_get_img_url_method(self):
        # Test the image URL generation
        achievement = Achievement.objects.create(
            club=self.club,
            cup='EPL',
            year=2022
        )
        expected_url = f'/static/cup_imgs/{CUP_CHOICES_DICT["EPL"][1]}'
        self.assertEqual(achievement.get_img_url(), expected_url)

    def test_str_representation(self):
        # Test the string representation of Achievement model
        achievement = Achievement.objects.create(
            club=self.club,
            cup='FA',
            year=2021
        )
        expected_str = f'Test Club won FA in 2021'
        self.assertEqual(str(achievement), expected_str)

def generate_random_string(length):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))

class ClubFormTest(TestCase):
    def setUp(self):
        os.makedirs('tmp', exist_ok=True)
        
    @override_settings(MEDIA_ROOT=os.path.join('tmp'))
    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT)

    @override_settings(MEDIA_ROOT=os.path.join('tmp'))
    def create_test_logo(self):
        with open('test_media/test_club_logo.png', 'rb') as logo_file:
            return SimpleUploadedFile(logo_file.name,
                                      logo_file.read(),
                                      content_type='image/png')

    def test_valid_data(self):
        logo = self.create_test_logo()
        form_data = {
            'name': 'Test Club',
            'established_year': 2000,
            'stadium': 'AN',
        }
        form = ClubForm(data=form_data, files={'logo': logo})
        self.assertTrue(form.is_valid())

    def test_empty_name(self):
        logo = self.create_test_logo()
        form_data = {
            'name': '',
            'established_year': 2000,
            'stadium': 'AN',
        }
        form = ClubForm(data=form_data, files={'logo': logo})
        self.assertFalse(form.is_valid())

    def test_name_valid_boundary(self):
        logo = self.create_test_logo()
        form_data = {
            'name': generate_random_string(255),
            'established_year': 2000,
            'stadium': 'AN',
        }
        form = ClubForm(data=form_data, files={'logo': logo})
        self.assertTrue(form.is_valid())

    def test_name_invalid_boundary(self):
        logo = self.create_test_logo()
        form_data = {
            'name': generate_random_string(256),
            'established_year': 2000,
            'stadium': 'AN',
        }
        form = ClubForm(data=form_data, files={'logo': logo})
        self.assertFalse(form.is_valid())

    def test_name_with_special_characters(self):
        logo = self.create_test_logo()
        form_data = {
            'name': '%^&*(213)',
            'established_year': 2000,
            'stadium': 'AN',
        }
        form = ClubForm(data=form_data, files={'logo': logo})
        self.assertFalse(form.is_valid())


    def test_invalid_established_year_future(self):
        future_year = date.today().year + 5
        logo = self.create_test_logo()
        form_data = {
            'name': 'Test Club',
            'established_year': future_year,
            'stadium': 'AN',
        }
        form = ClubForm(data=form_data, files={'logo': logo})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['established_year'], ["Invalid club's established year!"])

    def test_empty_stadium(self):
        logo = self.create_test_logo()
        form_data = {
            'name': 'Test Club',
            'established_year': 2000,
            'stadium': '',
        }
        form = ClubForm(data=form_data, files={'logo': logo})
        self.assertFalse(form.is_valid())

    def test_invalid_stadium(self):
        logo = self.create_test_logo()
        form_data = {
            'name': 'Test Club',
            'established_year': 2000,
            'stadium': 'XY',
        }
        form = ClubForm(data=form_data, files={'logo': logo})
        self.assertFalse(form.is_valid())

    def test_empty_logo(self):
        form_data = {
            'name': 'Test Club',
            'established_year': 2000,
            'stadium': 'AN',
        }
        form = ClubForm(data=form_data)
        self.assertFalse(form.is_valid())

class AchievementFormTest(TestCase):
    def setUp(self):
        self.club = Club.objects.create(name='Test Club')

    def test_valid_year(self):
        valid_year = date.today().year - 1
        form_data = {'cup': 'FA', 'year': valid_year}
        form = AchievementForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_future_year(self):
        future_year = date.today().year + 1
        form_data = {'cup': 'EPL', 'year': future_year}
        form = AchievementForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['year'], ["Invalid year"])

class ClubViewTest(TestCase):
    @override_settings(MEDIA_ROOT=os.path.join('tmp'))
    def setUp(self):
        os.makedirs('tmp', exist_ok=True)

        self.client = Client()

        self.admin = User.objects.create_user(username='admin', password='admin123')
        UserProfile.objects.create(user=self.admin, type='admin')

        self.club = self.create_test_club('Test Club')

        self.client.login(username='admin', password='admin123')

    @override_settings(MEDIA_ROOT=os.path.join('tmp'))
    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT)

    @override_settings(MEDIA_ROOT=os.path.join('tmp'))
    def create_test_club(self, name):
        with open('test_media/test_club_logo.png', 'rb') as logo_file:
            logo = SimpleUploadedFile(logo_file.name,
                                      logo_file.read(),
                                      content_type='image/png')
            return Club.objects.create(
                name=name,
                logo=logo,
                stadium='AN',
            )

    def test_update_clubs_status(self):
        update_clubs_status()
        self.assertTrue(Club.objects.filter(status='I').exists())

    def test_index_view(self):
        response = self.client.get(reverse('clubs:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clubs/index.html')

        self.assertIn('user', response.context)
        self.assertEqual(response.context['user'], self.admin)

        self.assertIsInstance(response.context['form'], ClubSearchForm)

        self.assertIn('clubs', response.context)
        self.assertEqual(len(response.context['clubs']), 1)

    def test_add_view(self):
        url = reverse('clubs:add')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clubs/add.html')

        with open('test_media/test_club_logo.png', 'rb') as logo_file:
            logo = SimpleUploadedFile(logo_file.name,
                                      logo_file.read(),
                                      content_type='image/png')
            data = {
                'name': 'New Club',
                'stadium': 'AN',
                'logo': logo
            }

            response = self.client.post(url, data, follow=True)
            self.assertEqual(response.status_code, 302)
            self.assertTemplateUsed(response, 'clubs/add.html')
            self.assertTrue(Club.objects.filter(name='New Club').exists())

            self.assertIn('user', response.context)
            self.assertEqual(response.context['user'], self.admin)

            self.assertIsInstance(response.context['club_form'], ClubForm)

            self.assertIn('clubs', response.context)
            self.assertEqual(len(response.context['clubs']), 1)

    # edit should be the same as add

    def test_detail_view(self):
        url = reverse('clubs:view', args=[self.club.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clubs/view.html')

        self.assertIn('user', response.context)
        self.assertEqual(response.context['user'], self.admin)

        self.assertIn('club', response.context)
        self.assertEqual(response.context['club'], self.club)

        self.assertIn('has_manager', response.context)
        self.assertFalse(response.context['has_manager'])

        self.assertIn('clubs', response.context)
        self.assertEqual(len(response.context['clubs']), 1)

    def test_delete_view(self):
        club_id = self.club.id
        response = self.client.post(reverse('clubs:delete', kwargs={'club_id': club_id}))
        self.assertEqual(response.status_code, 302)  # Redirects after deletion
        self.assertFalse(Club.objects.filter(id=club_id).exists())

    def test_search_view(self):
        response = self.client.get(reverse('clubs:search'), {'club_name': 'Test'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clubs/search.html') 

        self.assertIsInstance(response.context['form'], ClubSearchForm)
        
        self.assertIn('user', response.context)
        self.assertEqual(response.context['user'], self.admin)

        self.assertIn('clubs', response.context)
        self.assertEqual(len(response.context['clubs']), 1)
