import os
import time
from datetime import date
from django.conf import settings
from django.core.files import File
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from apps.auth.models import UserProfile
from apps.managers.models import Manager
from apps.clubs.models import Club
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select

class TestManagersManagement(StaticLiveServerTestCase):
    """
    This class contains automation tests for the Managers app.
    """
    def setUp(self):
        """
        This method sets up the test environment. It is run before each test method.
        """
        options = Options()
        options.add_argument("--headless=new")
        self.driver = webdriver.Chrome(options=options)
        self.driver.get(f"{self.live_server_url}/")
        self.driver.maximize_window()
        self.admin = User.objects.create_user(username='admin', password='admin123456')
        self.admin_profile = UserProfile.objects.create(user=self.admin, type='admin')
        self.login('admin', 'admin123456')
        self.create_club()
        self.navigate_to_managers()

    def tearDown(self):
        """
        This method cleans up after each test method.
        """
        self.driver.quit()

    def login(self, username, password):
        """
        This method logs in to the application as an admin
        Parameters:
            username (str): The username to log in with
            password (str): The password to log in with
        """
        username_field = self.driver.find_element(by=By.NAME, value="username")
        password_field = self.driver.find_element(by=By.NAME, value="password")
        submit_button = self.driver.find_element(by=By.XPATH, value="//input[@type='submit']")
        username_field.send_keys(username)
        password_field.send_keys(password)
        submit_button.click()

    def create_club(self):
        """
        This method creates a dummy club instance for testing.
        """
        with open("test_media/test_club_logo.png", 'rb') as f:
            logo_image = File(f)
            self.club = Club.objects.create(
                name="Liverpool", 
                logo=logo_image, 
                stadium="AN"
            )

    def navigate_to_managers(self):
        """
        This method navigates to the managers page.
        """
        managers_tab = self.driver.find_element(by=By.XPATH, value="//a[@href='/managers']")
        managers_tab.click()

    def fill_form(self, name, dob, club, nationality):
        """
        This method fills out the manager form.

        Parameters:
            name (str): The manager name
            dob (str): The manager's date of birth
            club (str): The manager's club
            nationality (str): The manager's nationality
        """
        try: 
            name_field = self.driver.find_element(by=By.ID, value="id_name")
            dob_field = self.driver.find_element(by=By.ID, value="id_dob")
            club_field = self.driver.find_element(by=By.ID, value="id_club")
            nationality_field = self.driver.find_element(by=By.ID, value="id_nationality")
            save_button = self.driver.find_element(by=By.XPATH, value="//button[@class='btn btn-primary w-100']")
        except NoSuchElementException as e:
            self.fail(f"Element not found: {e}")
        
        name_field.clear()
        dob_field.clear()
        
        name_field.send_keys(name)
        dob_field.send_keys(dob)
        
        club_select = Select(club_field)
        nationality_select = Select(nationality_field)
        club_select.select_by_visible_text(club)
        nationality_select.select_by_visible_text(nationality)
        save_button.click()

    def add_manager(self, name, dob, club, nationality):
        """
        This method adds a new manager through the UI by automating with Selenium

        Parameters:
            name (str): The manager name
            dob (str): The manager's date of birth
            club (str): The manager's club
            nationality (str): The manager's nationality
        """
        add_manager_button = self.driver.find_element(by=By.XPATH, value="//button[text()='Add manager']")
        add_manager_button.click()
        self.fill_form(name, dob, club, nationality)

    def test_add_manager(self):
        """
        This method tests the addition of a new manager
        """
        self.add_manager("John Doe", "01011980", "Liverpool", "English")
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".alert.alert-success")))
            success_message = self.driver.find_element(by=By.CSS_SELECTOR, value=".alert.alert-success")
        except (TimeoutException, NoSuchElementException) as e:
            self.fail(f"Test failed: {e}")  
        self.assertEqual(success_message.text, 'Manager was added successfully!', "The success message was not displayed")
        
        manager = Manager.objects.filter(name="John Doe").first()
        self.assertIsNotNone(manager, "An added manager was not found")

    def test_edit_manager(self):
        """
        This method tests the editing of a manager
        """
        self.manager = Manager.objects.create(
            name="John Doe",
            dob="1975-10-29",
            club=self.club,
            nationality="Croatian",
        )
        self.driver.refresh()
        try:
            edit_button = self.driver.find_element(by=By.ID, value=f"edit-{self.manager.id}")
        except NoSuchElementException as e:
            self.fail(f"Test failed: {e}")
        edit_button.click()
        self.fill_form("Jane Doe", "02021974", "Liverpool", "English")
        updated_manager = Manager.objects.get(id=self.manager.id)
        self.assertEqual(updated_manager.name, "Jane Doe", "The manager's name was not updated correctly")
        
    def test_delete_manager(self):
        """
        This method tests the deletion of a manager
        """
        self.manager = Manager.objects.create(
            name="John Doe",
            dob="1976-10-29",
            club=self.club,
            nationality="Croatian",
        )
        self.driver.refresh()
        try:
            delete_button = self.driver.find_element(by=By.ID, value=f"delete-{self.manager.id}")
        except NoSuchElementException as e:
            self.fail(f"Test failed: {e}")
        delete_button.click()

        alert = self.driver.switch_to.alert
        alert.accept()
        # add a little delay for the db to update
        time.sleep(2)
        with self.assertRaises(Manager.DoesNotExist):
            Manager.objects.get(id=self.manager.id)

class TestManagersSearch(StaticLiveServerTestCase):
    def setUp(self):
        """
        This method sets up the test environment. It is run before each test method.
        """
        options = Options()
        options.add_argument("--headless=new")
        self.driver = webdriver.Chrome(options=options)
        self.driver.get(f"{self.live_server_url}/")
        self.driver.maximize_window()
        self.user = User.objects.create_user(username='user', password='user123456')
        self.user_profile = UserProfile.objects.create(user=self.user, type='user')
        self.login('user', 'user123456')
        self.clubs = list()
        self.clubs.append(self.create_club("Manchester United", "test_media/test_club_logo.png", "OT"))
        self.clubs.append(self.create_club("Liverpool", "test_media/test_club_logo.png", "AN"))
        self.clubs.append(self.create_club("Manchester City", "test_media/test_club_logo.png", "ET"))
        self.navigate_to_managers()

    def tearDown(self):
        """
        This method cleans up after each test method.
        """
        self.driver.quit()

    def login(self, username, password):
        """
        This method logs in to the application as an user
        Parameters:
            username (str): The username 
            password (str): The password 
        """
        username_field = self.driver.find_element(by=By.NAME, value="username")
        password_field = self.driver.find_element(by=By.NAME, value="password")
        submit_button = self.driver.find_element(by=By.XPATH, value="//input[@type='submit']")
        username_field.send_keys(username)
        password_field.send_keys(password)
        submit_button.click()

    def navigate_to_managers(self):
        """
        This method navigates to the managers page.
        """
        managers_tab = self.driver.find_element(by=By.XPATH, value="//a[@href='/managers']")
        managers_tab.click()

    def create_club(self, name, logo_path, stadium):
        """
        This method adds a new club in the database using Django's ORM
        Parameters:
            name (str): The name of the club
            logo (str): The path to the club logo image
            stadium (str): The name of the club stadium
        """
        with open(logo_path, 'rb') as f:
            logo_image = File(f)
            return Club.objects.create(
                name=name,
                logo=logo_image,
                stadium=stadium,
            )

    def populate_managers(self, *args):
        """
        This method populates the test database with some Manager instances. (this method serves for search functionality testing)
        """
        for i, arg in enumerate(args):
            Manager.objects.create(
                name=arg,
                dob="1976-10-29",
                club=self.clubs[i],
                nationality="English",
            )

    def test_search_returns_single_manager(self):
        """
        This method tests if the search functionality returns a single manager when the search query matches exactly one manager.
        """
        self.populate_managers("Jurgen Klopp", "Pep Guardiola", "Erik Ten-hag")
        self.driver.refresh()
        self.query = "Klo"
        try:
            search_bar = self.driver.find_element(by=By.XPATH, value="//input[@placeholder='Search']")
            search_button = self.driver.find_element(by=By.XPATH, value="//button[text()='SEARCH']")
            search_bar.send_keys(self.query)
            search_button.click()
            
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//span[@class='font-weight-bold']")))
            manager_name_elements = self.driver.find_elements(by=By.XPATH, value="//span[@class='font-weight-bold']")
            assert len(manager_name_elements) == 1, "There are more than 1 manager displayed"
            assert self.query in manager_name_elements[0].text, f"The manager name does not contain the search query: '{self.query}'"
            
        except NoSuchElementException as e:
            self.fail(f"Test failed: {e}")

    def test_search_returns_multiple_managers(self):
        """
        This method tests if the search functionality returns multiple managers when the search query matches more than one manager.
        """
        self.populate_managers("Jurgen Klopp", "Erik Nine-hag", "Erik Ten-hag")
        self.driver.refresh()
        self.query = "Erik"
        try:
            search_bar = self.driver.find_element(by=By.XPATH, value="//input[@placeholder='Search']")
            search_button = self.driver.find_element(by=By.XPATH, value="//button[text()='SEARCH']")
            search_bar.send_keys(self.query)
            search_button.click()
            
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//span[@class='font-weight-bold']")))
            manager_name_elements = self.driver.find_elements(by=By.XPATH, value="//span[@class='font-weight-bold']")
            assert len(manager_name_elements) == 2, "Expected 2 managers, but got {0}".format(len(manager_name_elements))
            for manager_name_element in manager_name_elements:
                assert self.query in manager_name_element.text, f"Manager name does not contain '{self.query}'"
        except NoSuchElementException as e:
            self.fail(f"Test failed: {e}")

    def test_search_returns_no_manager(self):
        """
        This method tests if the search functionality returns no managers when the search query does not match any manager.
        """
        self.populate_managers("Jurgen Klopp", "Pep Guardiola")
        self.driver.refresh()
        self.query = "Zinchenko"
        try:
            search_bar = self.driver.find_element(by=By.XPATH, value="//input[@placeholder='Search']")
            search_button = self.driver.find_element(by=By.XPATH, value="//button[text()='SEARCH']")
            search_bar.send_keys(self.query)
            search_button.click()
            display_message = self.driver.find_element(by=By.XPATH, value="//h3[@class='display-4 font-select']")
            assert display_message.text == "No managers found.", "The search result is wrong"

        except NoSuchElementException as e:
            self.fail(f"Test failed: {e}")