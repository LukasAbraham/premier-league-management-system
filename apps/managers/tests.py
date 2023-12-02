import os
import shutil
from django.conf import settings

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase, override_settings

from apps.clubs.models import Club
from .models import Manager
from .views import index

class ManagerModelTest(TestCase):
    def setUp(self):
        self.club = Club.objects.create(name='Test Club')
        self.manager = Manager.objects.create(name='Test Manager',
                                              nationality='English',
                                              dob='1970-01-01',
                                              club=self.club)

    # Create
    def test_manager_creation(self):
        self.assertTrue(isinstance(self.manager, Manager))
        self.assertEqual(self.manager.__str__(), self.manager.name)

    # Update
    def test_manager_name_update(self):
        new_name = 'Updated Manager'
        self.manager.name = new_name
        self.manager.save()
        self.assertEqual(self.manager.name, new_name)

    def test_manager_nationality_update(self):
        new_nationality = 'Spanish'
        self.manager.nationality = new_nationality
        self.manager.save()
        self.assertEqual(self.manager.nationality, new_nationality)

    def test_manager_dob_update(self):
        new_dob = '1980-05-15'
        self.manager.dob = new_dob
        self.manager.save()
        self.assertEqual(self.manager.dob, new_dob)

    def test_manager_club_update(self):
        new_club = Club.objects.create(name='Another Test Club')
        self.manager.club = new_club
        self.manager.save()
        self.assertEqual(self.manager.club, new_club)

    # Delete
    def test_manager_deletion(self):
        manager_id = self.manager.id;
        self.assertIsNotNone(manager_id)
        self.manager.delete()
        self.assertEqual(Manager.objects.count(), 0)
        with self.assertRaises(Manager.DoesNotExist):
            Manager.objects.get(id=manager_id)

class ManagerViewsTest(TestCase):
    @override_settings(MEDIA_ROOT=os.path.join('tmp'))
    def setUp(self):
        os.makedirs('tmp', exist_ok=True)

        self.rf = RequestFactory()
        self.user = User.objects.create(username='testuser',
                                        password='testpassword')

        club_logo_path = 'test_media/test_club_logo.png'
        club_logo_name = 'test_club_logo.png'
        with open(club_logo_path, 'rb') as logo_file:
            logo = SimpleUploadedFile(club_logo_name,
                                      logo_file.read(),
                                      content_type='image/png')
            self.club = Club.objects.create(name='Test Club',logo=logo)

        manager_image_path = 'test_media/test_manager.png'
        manager_image_name = 'test_manager.png'
        with open(manager_image_path, 'rb') as image_file:
            image = SimpleUploadedFile(manager_image_name,
                                       image_file.read(),
                                       content_type='image/png')
            self.manager = Manager.objects.create(name='Test Manager',
                                                  nationality='English',
                                                  dob='1970-01-01',
                                                  club=self.club,
                                                  image=image)
    @override_settings(MEDIA_ROOT=os.path.join('tmp'))
    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT)

    def test_index_view(self):
        get_request = self.rf.get('/managers/')
        get_request.user = self.user
        get_response = index(get_request)

        self.assertEqual(get_response.status_code, 200)

