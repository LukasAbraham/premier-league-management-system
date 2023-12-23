import os
import time
from datetime import date
from django.conf import settings
from django.core.files import File
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from apps.clubs.models import Club
from apps.auth.models import UserProfile
from apps.players.models import Player, PlayerStats
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

class TestPlayersManagement(StaticLiveServerTestCase):
    """
    This class contains automation tests for the Players app.
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
        self.navigate_to_players()

    def tearDown(self):
        """
        This method cleans up after each test method.
        """
        self.driver.quit()

    def login(self, username, password):
        """
        This method logs in to the application as an admin

        Parameters:
            username (str): The username to sign in with.
            password (str): The password to sign in with.
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

    def navigate_to_players(self):
        """
        This method navigates to the players page.
        """
        players_tab = self.driver.find_element(by=By.XPATH, value="//a[@href='/players']")
        players_tab.click()

    def fill_form(self, name, dob, weight, height, club, nationality, position):
        """
        This method fills out the player form.

        Parameters:
            name (str): The player name
            dob (str): The player's date of birth
            weight (str): The player's weight
            height (str): The player's height
            club (str): The player's club
            nationality (str): The player's nationality
            position (str): The player's position on the pitch
        """
        try: 
            name_field = self.driver.find_element(by=By.ID, value="id_name")
            dob_field = self.driver.find_element(by=By.ID, value="id_dob")
            weight_field = self.driver.find_element(by=By.ID, value="id_weight")
            height_field = self.driver.find_element(by=By.ID, value="id_height")
            club_field = self.driver.find_element(by=By.ID, value="id_club")
            nationality_field = self.driver.find_element(by=By.ID, value="id_nationality")
            position_field = self.driver.find_element(by=By.ID, value="id_position")
            save_button = self.driver.find_element(by=By.XPATH, value="//button[@class='btn btn-primary w-100']")
        except NoSuchElementException as e:
            self.fail(f"Element not found: {e}")
        
        name_field.clear()
        dob_field.clear()
        weight_field.clear()
        height_field.clear()
        
        name_field.send_keys(name)
        dob_field.send_keys(dob)
        weight_field.send_keys(weight)
        height_field.send_keys(height)
        
        club_select = Select(club_field)
        nationality_select = Select(nationality_field)
        position_select = Select(position_field)
        club_select.select_by_visible_text(club)
        nationality_select.select_by_visible_text(nationality)
        position_select.select_by_visible_text(position)
        save_button.click()

    def add_player(self, name, dob, weight, height, club, nationality, position):
        """
        This method adds a new player through the UI by automating with Selenium

        Parameters:
            name (str): The player name
            dob (str): The player's date of birth
            weight (str): The player's weight
            height (str): The player's height
            club (str): The player's club
            nationality (str): The player's nationality
            position (str): The player's position
        """
        add_player_button = self.driver.find_element(by=By.XPATH, value="//button[text()='Add player']")
        add_player_button.click()
        self.fill_form(name, dob, weight, height, club, nationality, position)

    def test_add_player(self):
        """
        This method tests the addition of a new player.
        """
        self.add_player("John Doe", "01012000", 70, 180, "Liverpool", "English", "Forward")
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".alert.alert-success")))
            success_message = self.driver.find_element(by=By.CSS_SELECTOR, value=".alert.alert-success")
        except (TimeoutException, NoSuchElementException) as e:
            self.fail(f"Test failed: {e}")  
        self.assertEqual(success_message.text, 'Player was added successfully!', "The success message was not displayed")
        
        player = Player.objects.filter(name="John Doe").first()
        self.assertIsNotNone(player, "An added player was not found")

    def test_edit_player(self):
        """
        This method tests the editing of a player.
        """
        self.player = Player.objects.create(
            name="John Doe",
            dob="1999-10-29",
            weight=80,
            height=180,
            club=self.club,
            nationality="Croatian",
            position="FW"
        )
        self.driver.refresh()
        try:
            edit_button = self.driver.find_element(by=By.ID, value=f"edit-{self.player.id}")
        except NoSuchElementException as e:
            self.fail(f"Test failed: {e}")
        edit_button.click()
        self.fill_form("Jane Doe", "02021999", 70, 180, "Liverpool", "English", "Forward")  
        updated_player = Player.objects.get(id=self.player.id)
        assert updated_player.name == "Jane Doe", "The player's name was not updated correctly"
        
    def test_delete_player(self):
        """
        This method tests the deletion of a player.
        """
        self.player = Player.objects.create(
            name="John Doe",
            dob="1999-10-29",
            weight=80,
            height=180,
            club=self.club,
            nationality="Croatian",
            position="FW"
        )
        self.driver.refresh()
        try:
            delete_button = self.driver.find_element(by=By.ID, value=f"delete-{self.player.id}")
        except NoSuchElementException as e:
            self.fail(f"Test failed: {e}")
        delete_button.click()

        alert = self.driver.switch_to.alert
        alert.accept()
        # add a little delay for the db to update
        time.sleep(2)
        with self.assertRaises(Player.DoesNotExist):
            Player.objects.get(id=self.player.id)

class TestPlayersSearch(StaticLiveServerTestCase):
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
        self.create_club()
        self.navigate_to_players()

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

    def navigate_to_players(self):
        """
        This method navigates to the players page.
        """
        players_tab = self.driver.find_element(by=By.XPATH, value="//a[@href='/players']")
        players_tab.click()

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

    def populate_players(self, *args):
        """
        This method populates the test database with some Player instances. (this method serves for search functionality testing)
        """
        for i, arg in enumerate(args):
            Player.objects.create(
                name=arg,
                dob="1999-10-29",
                weight=80,
                height=180,
                club=self.club,
                nationality="English",
                position="FW"
            )

    def test_search_returns_single_player(self):
        """
        This method tests if the search functionality returns a single player when the search query matches exactly one player.
        """
        self.populate_players("Mohamed Salah", "Khvicha Kvaratskhelia", "Dejan Kulusevski")
        self.driver.refresh()
        self.query = "Mo"
        try:
            search_bar = self.driver.find_element(by=By.XPATH, value="//input[@placeholder='Search']")
            search_button = self.driver.find_element(by=By.XPATH, value="//button[text()='SEARCH']")
            search_bar.send_keys(self.query)
            search_button.click()
            
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//span[@class='font-weight-bold']")))
            player_name_elements = self.driver.find_elements(by=By.XPATH, value="//span[@class='font-weight-bold']")
            assert len(player_name_elements) == 1, "There are more than 1 player displayed"
            assert self.query in player_name_elements[0].text, f"The player name does not contain the search query: '{self.query}'"
            
        except NoSuchElementException as e:
            self.fail(f"Test failed: {e}")

    def test_search_returns_multiple_players(self):
        """
        This method tests if the search functionality returns multiple players when the search query matches more than one player.
        """
        self.populate_players("Mohamed Salah", "Marcelo Salas", "Dejan Kulusevski")
        self.driver.refresh()
        self.query = "Sala"
        try:
            search_bar = self.driver.find_element(by=By.XPATH, value="//input[@placeholder='Search']")
            search_button = self.driver.find_element(by=By.XPATH, value="//button[text()='SEARCH']")
            search_bar.send_keys(self.query)
            search_button.click()
            
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//span[@class='font-weight-bold']")))
            player_name_elements = self.driver.find_elements(by=By.XPATH, value="//span[@class='font-weight-bold']")
            assert len(player_name_elements) == 2, "Expected 2 players, but got {0}".format(len(player_name_elements))
            for player_name_element in player_name_elements:
                assert self.query in player_name_element.text, f"Player name does not contain the search query: '{self.query}'"
        except NoSuchElementException as e:
            self.fail(f"Test failed: {e}")

    def test_search_returns_no_player(self):
        """
        This method tests if the search functionality returns no players when the search query does not match any player.
        """
        self.populate_players("Mohamed Salah", "Thiago Alcantara")
        self.driver.refresh()
        self.query = "Pippo"
        try:
            search_bar = self.driver.find_element(by=By.XPATH, value="//input[@placeholder='Search']")
            search_button = self.driver.find_element(by=By.XPATH, value="//button[text()='SEARCH']")
            search_bar.send_keys(self.query)
            search_button.click()
            display_message = self.driver.find_element(by=By.XPATH, value="//h3[@class='display-4 font-select']")
            assert display_message.text == "No players found.", "The search result is wrong"

        except NoSuchElementException as e:
            self.fail(f"Test failed: {e}")