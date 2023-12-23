import os
import time
from django.conf import settings
from django.core.files import File
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from apps.auth.models import UserProfile
from apps.clubs.models import Club
from apps.players.models import Player
from apps.managers.models import Manager
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select

class TestClubsManagement(StaticLiveServerTestCase):
    """
    This class contains automation tests for the Clubs app.
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
        self.navigate_to_clubs()

    def tearDown(self):
        """
        This method cleans up after each test method.
        """
        self.driver.quit()

    def login(self, username, password):
        """
        This method logs in to the application as an admin
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

    def navigate_to_clubs(self):
        """
        This method navigates to the clubs page.
        """
        clubs_tab = self.driver.find_element(by=By.XPATH, value="//a[@href='/clubs']")
        clubs_tab.click()

    def fill_form(self, name, logo, stadium):
        """
        This method fills out the club form.

        Parameters:
            name (str): The name of the club.
            logo (str): The path to the logo image.
            stadium (str): The name of the stadium.
        """
        try: 
            name_field = self.driver.find_element(by=By.ID, value="id_name")
            logo_field = self.driver.find_element(by=By.ID, value="id_logo")
            stadium_field = self.driver.find_element(by=By.ID, value="id_stadium")
            save_button = self.driver.find_element(by=By.XPATH, value="//button[@class='btn btn-primary w-100']")
        except NoSuchElementException as e:
            self.fail(f"Element not found: {e}")

        base_dir = settings.BASE_DIR
        logo_path = os.path.join(base_dir, logo)
        
        name_field.clear()
        logo_field.clear()
        
        name_field.send_keys(name)
        logo_field.send_keys(logo_path)
        
        stadium_select = Select(stadium_field)
        stadium_select.select_by_visible_text(stadium)
        save_button.click()

    def add_club(self, name, logo, stadium):
        """
        This method adds a new club through the UI by automating with Selenium

        Parameters:
            name (str): The name of the club
            logo (str): The path to the club logo image.
            stadium (str): The name of the club stadium.
        """
        add_club_button = self.driver.find_element(by=By.XPATH, value="//button[@class='btn btn-primary mr-3 mt-2']")
        add_club_button.click()
        self.fill_form(name, logo, stadium)

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
            self.club = Club.objects.create(
                name=name,
                logo=logo_image,
                stadium=stadium,
            )

    def test_add_club(self):
        """
        This method tests the addition of a new club.
        """
        self.add_club("Manchester City", "test_media/test_club_logo.png", "Etihad Stadium")
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".alert.alert-success")))
            success_message = self.driver.find_element(by=By.CSS_SELECTOR, value=".alert.alert-success")
        except (TimeoutException, NoSuchElementException) as e:
            self.fail(f"Test failed: {e}")  
        self.assertEqual(success_message.text, 'Club was created successfully!', "The success message was not displayed")
        
        club = Club.objects.filter(name="Manchester City").first()
        self.assertIsNotNone(club, "An added club was not found")

    def test_edit_club(self):
        """
        This method tests the editing of a club.
        """
        self.create_club(name="Liverpool", logo_path="test_media/test_club_logo.png", stadium="AN")
        self.driver.refresh()
        try:
            edit_button = self.driver.find_element(by=By.ID, value=f"edit-{self.club.id}")
        except NoSuchElementException as e:
            self.fail(f"Test failed: {e}")
        edit_button.click()
        self.fill_form("Manchester City", "test_media/test_club_logo.png", "Etihad Stadium")    
        updated_club = Club.objects.get(id=self.club.id)
        self.assertEqual(updated_club.name, "Manchester City", "The club's name was not updated correctly")
        
    def test_delete_club(self):
        """
        This method tests the deletion of a club.
        """
        self.create_club(name="Everton", logo_path="test_media/test_club_logo.png", stadium="LS")
        self.driver.refresh()
        try:
            delete_button = self.driver.find_element(by=By.ID, value=f"delete-{self.club.id}")
        except NoSuchElementException as e:
            self.fail(f"Test failed: {e}")
        delete_button.click()
        alert = self.driver.switch_to.alert
        alert.accept()
        # add a little delay for the db to update
        time.sleep(2)
        with self.assertRaises(Club.DoesNotExist):
            Club.objects.get(id=self.club.id)
            
    def test_delete_player_from_club(self):
        """
        This method tests the deletion of a player in the club view screen
        """
        self.create_club(name="Everton", logo_path="test_media/test_club_logo.png", stadium="ET")
        self.player = Player.objects.create(
            name="John Doe",
            dob = "1999-10-29",
            weight=80,
            height=180,
            club=self.club,
            nationality="Croatian",
            position="FW"
        )
        self.driver.refresh()
        try:
            selected_club = self.driver.find_element(by=By.XPATH, value="//span[text()='Everton']")
        except NoSuchElementException as e:
            self.fail(f"Test failed: {e}")
        selected_club.click()
        try:
            player_delete_button = self.driver.find_element(by=By.ID, value=f"player-delete-{self.player.id}")
        except NoSuchElementException as e:
            self.fail(f"Test failed: {e}")
        player_delete_button.click()
        alert = self.driver.switch_to.alert
        alert.accept()
        time.sleep(1)
        assert self.driver.title == "Clubs"
        
    def test_delete_manager_from_club(self):
        """
        This method tests the deletion of a manager in the club view screen
        """
        self.create_club(name="Everton", logo_path="test_media/test_club_logo.png", stadium="ET")
        self.manager = Manager.objects.create(
            name="John Doe",
            dob = "1975-10-29",
            club=self.club,
            nationality="Croatian",
        )
        self.driver.refresh()
        try:
            selected_club = self.driver.find_element(by=By.XPATH, value="//span[text()='Everton']")
        except NoSuchElementException as e:
            self.fail(f"Test failed: {e}")
        selected_club.click()
        try:
            manager_delete_button = self.driver.find_element(by=By.ID, value=f"manager-delete-{self.manager.id}")
        except NoSuchElementException as e:
            self.fail(f"Test failed: {e}")
        manager_delete_button.click()
        alert = self.driver.switch_to.alert
        alert.accept()
        time.sleep(1)
        assert self.driver.title == "Clubs"
        
    def test_delete_club_from_view_page(self):
        """
        This method tests the deletion of a club in its view page.
        """
        self.create_club(name="Everton", logo_path="test_media/test_club_logo.png", stadium="LS")
        self.driver.refresh()
        try:
            selected_club = self.driver.find_element(by=By.XPATH, value="//span[text()='Everton']")
        except NoSuchElementException as e:
            self.fail(f"Test failed: {e}")
        selected_club.click()
        try:
            delete_button = self.driver.find_element(by=By.ID, value="club-delete")
        except NoSuchElementException as e:
            self.fail(f"Test failed: {e}")
        delete_button.click()
        try: 
            WebDriverWait(self.driver, 5).until(EC.alert_is_present())
            alert = self.driver.switch_to.alert
            alert.accept()
        except TimeoutException:
            self.fail("No alert popped up")
        time.sleep(2)
        with self.assertRaises(Club.DoesNotExist):
            Club.objects.get(id=self.club.id)
        
class TestClubsSearch(StaticLiveServerTestCase):
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
        self.navigate_to_clubs()

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

    def navigate_to_clubs(self):
        """
        This method navigates to the clubs page.
        """
        clubs_tab = self.driver.find_element(by=By.XPATH, value="//a[@href='/clubs']")
        clubs_tab.click()

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
            Club.objects.create(
                name=name,
                logo=logo_image,
                stadium=stadium,
            )

    def populate_clubs(self, *args):
        """
        This method populates the test database with some Club instances. (this method serves for search functionality testing)
        """
        for arg in args:
            self.create_club(name=arg, logo_path="test_media/test_club_logo.png", stadium="OT")

    def test_search_returns_single_club(self):
        """
        This method tests if the search functionality returns a single club when the search query matches exactly one club.
        """
        self.populate_clubs("Liverpool", "Manchester United", "Manchester City")
        self.driver.refresh()
        self.query = "Liv"
        try:
            search_bar = self.driver.find_element(by=By.XPATH, value="//input[@placeholder='Search']")
            search_button = self.driver.find_element(by=By.XPATH, value="//button[text()='SEARCH']")
            search_bar.send_keys(self.query)
            search_button.click()
            
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//span[@class='font-weight-bold']")))
            club_name_elements = self.driver.find_elements(by=By.XPATH, value="//span[@class='font-weight-bold']")
            assert len(club_name_elements) == 1, "There are more than 1 club displayed"
            assert self.query in club_name_elements[0].text, f"The club name does not contain the search query: '{self.query}'"
            
        except NoSuchElementException as e:
            self.fail(f"Test failed: {e}")

    def test_search_returns_multiple_clubs(self):
        """
        This method tests if the search functionality returns multiple clubs when the search query matches more than one club.
        """
        self.populate_clubs("Liverpool", "Manchester United", "Manchester City")
        self.driver.refresh()
        self.query = "Man"
        try:
            search_bar = self.driver.find_element(by=By.XPATH, value="//input[@placeholder='Search']")
            search_button = self.driver.find_element(by=By.XPATH, value="//button[text()='SEARCH']")
            search_bar.send_keys(self.query)
            search_button.click()
            
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//span[@class='font-weight-bold']")))
            club_name_elements = self.driver.find_elements(by=By.XPATH, value="//span[@class='font-weight-bold']")
            assert len(club_name_elements) == 2, "Expected 2 clubs, but got {0}".format(len(club_name_elements))
            for club_name_element in club_name_elements:
                assert self.query in club_name_element.text, f"Club name does not contain '{self.query}'"
        except NoSuchElementException as e:
            self.fail(f"Test failed: {e}")

    def test_search_returns_no_club(self):
        """
        This method tests if the search functionality returns no clubs when the search query does not match any club.
        """
        self.populate_clubs("Liverpool", "Manchester City")
        self.driver.refresh()
        self.query = "Zha"
        try:
            search_bar = self.driver.find_element(by=By.XPATH, value="//input[@placeholder='Search']")
            search_button = self.driver.find_element(by=By.XPATH, value="//button[text()='SEARCH']")
            search_bar.send_keys(self.query)
            search_button.click()
            display_message = self.driver.find_element(by=By.XPATH, value="//h3[@class='display-4 font-select']")
            assert display_message.text == "No clubs found.", "The search result is wrong"

        except NoSuchElementException as e:
            self.fail(f"Test failed: {e}")