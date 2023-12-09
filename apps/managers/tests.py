import os
import shutil
import random
import string
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
from .models import Manager
from .forms import ManagerForm, ManagerSearchForm

class ManagerModelTest(TestCase):
    def setUp(self):
        self.club = Club.objects.create(name='Test Club')
        self.manager = Manager.objects.create(
            name='Test Manager',
            nationality='English',
            dob=date(1970, 1, 1),
            club=self.club
        )

    def test_creating_manager(self):
        self.assertTrue(isinstance(self.manager, Manager))
        self.assertEqual(self.manager.__str__(), self.manager.name)

    def test_updating_manager(self):
        new_name = 'Updated Manager'
        self.manager.name = new_name
        self.manager.save()
        self.assertEqual(self.manager.name, new_name)

        new_nationality = 'Spanish'
        self.manager.nationality = new_nationality
        self.manager.save()
        self.assertEqual(self.manager.nationality, new_nationality)

        new_dob = date(1980, 5, 15)
        self.manager.dob = new_dob
        self.manager.save()
        self.assertEqual(self.manager.dob, new_dob)

        new_club = Club.objects.create(name='Another Test Club')
        self.manager.club = new_club
        self.manager.save()
        self.assertEqual(self.manager.club, new_club)

    def test_deleting_manager(self):
        self.assertIsNotNone(self.manager.id)
        self.manager.delete()
        self.assertEqual(Manager.objects.count(), 0)
        with self.assertRaises(Manager.DoesNotExist):
            Manager.objects.get(id=self.manager.id)

def generate_random_string(length):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))

class ManagerFormsTests(TestCase):
    def setUp(self):
        Regulation.objects.get_or_create(pk=1)
        self.club = Club.objects.create(name='Test Club')

    def test_initial_values(self):
        form = ManagerForm()
        self.assertEqual(form.fields['dob'].initial, date.today())
        self.assertIsInstance(form.fields['dob'].widget, widgets.DateInput)

    def test_valid_data(self):
        form = ManagerForm(data={
            'name': 'Test Manager',
            'nationality': 'English',
            'dob': date(1970, 10, 10),
            'club': self.club.id,
        })
        self.assertTrue(form.is_valid())

    """
    Test manager name field
    """
    def test_name_with_special_characters(self):
        form = ManagerForm(data={
            'name': '123&*!*@#[]',
            'nationality': 'English',
            'dob': date(1970, 10, 10),
            'club': self.club.id,
        })
        self.assertFalse(form.is_valid())

    def test_name_empty(self):
        form = ManagerForm(data={
            'name': '',
            'nationality': 'English',
            'dob': date(1970, 10, 10),
            'club': self.club.id,
        })
        self.assertFalse(form.is_valid())

    def test_name_valid_boundary(self):
        form = ManagerForm(data={
            'name': generate_random_string(255),
            'nationality': 'English',
            'dob': date(1970, 10, 10),
            'club': self.club.id,
        })
        self.assertTrue(form.is_valid())

    def test_name_invalid_boundary(self):
        form = ManagerForm(data={
            'name': generate_random_string(256),
            'nationality': 'English',
            'dob': date(1970, 10, 10),
            'club': self.club.id,
        })
        self.assertFalse(form.is_valid())

    """
    Test nationality field
    """
    def test_nationality_empty(self):
        form = ManagerForm(data={
            'name': 'Test Manager',
            'nationality': '',
            'dob': date(1970, 10, 10),
            'club': self.club.id,
        })
        self.assertFalse(form.is_valid())

    """
    Test dob field
    """
    def test_dob_empty(self):
        form = ManagerForm(data={
            'name': 'Test Manager',
            'nationality': 'English',
            'dob': '',
            'club': self.club.id,
        })
        self.assertFalse(form.is_valid())

    def test_dob_invalid(self):
        form = ManagerForm(data={
            'name': 'Test Manager',
            'nationality': 'English',
            'dob': '1999-2-29',
            'club': self.club.id,
        })
        self.assertFalse(form.is_valid())

    """
    Test club field
    """
    def test_club_empty(self):
        form = ManagerForm(data={
            'name': 'Test Manager',
            'nationality': 'English',
            'dob': date(1970, 10, 10),
            'club': '',
        })
        self.assertFalse(form.is_valid())

class ManagerViewsTest(TestCase):
    @override_settings(MEDIA_ROOT=os.path.join('tmp'))
    def setUp(self):
        """
        Create a temporary directory for MEDIA_ROOT called /tmp.
        The uploaded images from the club and manager creation will be saved
        in /tmp.
        """
        os.makedirs('tmp', exist_ok=True)

        self.client = Client()

        self.admin = User.objects.create_user(username='admin', password='admin123')
        UserProfile.objects.create(user=self.admin, type='admin')

        with open('test_media/test_club_logo.png', 'rb') as logo_file:
            logo = SimpleUploadedFile(logo_file.name,
                                      logo_file.read(),
                                      content_type='image/png')
            self.club1 = Club.objects.create(name='Test Club 1', logo=logo)
            self.club2 = Club.objects.create(name='Test Club 2', logo=logo)
            self.club3 = Club.objects.create(name='Test Club 3', logo=logo)

        with open('test_media/test_manager.png', 'rb') as image_file:
            image = SimpleUploadedFile(image_file.name,
                                       image_file.read(),
                                       content_type='image/png')
            self.manager1 = Manager.objects.create(
                name='Test Manager 1',
                nationality='English',
                dob=date(1970, 1, 1),
                club=self.club1,
                image=image
            )
            self.manager2 = Manager.objects.create(
                name='Test Manager 2',
                nationality='Spanish',
                dob=date(1980, 2, 2),
                club=self.club2,
                image=image
            )

        # Login with admin priviledges
        self.client.login(username='admin', password='admin123')

    @override_settings(MEDIA_ROOT=os.path.join('tmp'))
    def tearDown(self):
        """
        Delete the /tmp directory after running all tests.
        """
        shutil.rmtree(settings.MEDIA_ROOT)

    def test_index_view(self):
        url = reverse('managers:index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'managers/index.html')
        self.assertContains(response, self.manager1.name)

    @override_settings(MEDIA_ROOT=os.path.join('tmp'))
    def test_add_view(self):
        url = reverse('managers:add')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        with open('test_media/test_manager.png', 'rb') as image_file:
            image = SimpleUploadedFile(image_file.name,
                                       image_file.read(),
                                       content_type='image/png')

            data = {
                'name': 'New Manager',
                'nationality': 'English',
                'dob': '1978-10-10',
                'club': self.club3.id,
                'image': image
            }

            response = self.client.post(url, data, follow=True)
            self.assertEqual(response.status_code, 302) # Expect redirection
            self.assertTemplateUsed(response, 'managers/add.html')
            self.assertTrue(Manager.objects.filter(name='New Manager').exists())

    def test_detail_view(self):
        url = reverse('managers:view', args=[self.manager1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'managers/view.html')
        self.assertEqual(response.context['user'], self.admin)
        self.assertEqual(response.context['manager'], self.manager1)

    @override_settings(MEDIA_ROOT=os.path.join('tmp'))
    def test_edit_view(self):
        url = reverse('managers:edit', args=[self.manager1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'managers/add.html')

        with open('test_media/test_manager.png', 'rb') as image_file:
            image = SimpleUploadedFile(image_file.name,
                                       image_file.read(),
                                       content_type='image/png')
            data = {
                'name': 'Updated Manager',
                'nationality': self.manager1.nationality,
                'dob': self.manager1.dob,
                'club': self.manager1.club.id,
                'image': image
            }

            response = self.client.post(url, data, follow=True)
            self.assertEqual(response.status_code, 302)
            self.manager1.refresh_from_db()
            self.assertEqual(self.manager1.name, 'Updated Manager')

    def test_delete_view(self):
        url = reverse('managers:delete', args=[self.manager1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302) # Expecting a redirect
        self.assertFalse(Manager.objects.filter(id=self.manager1.id).exists())

    def test_search_view(self):
        url = reverse('managers:search')
        response = self.client.get(url, {'manager_name': "Test Manager 1"})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'managers/search.html')
        self.assertIn(self.manager1, response.context['found_managers'])
        self.assertNotIn(self.manager2, response.context['found_managers'])

