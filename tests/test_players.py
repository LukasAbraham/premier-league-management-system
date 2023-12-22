import os
import time
from datetime import date
from django.conf import settings
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

class TestPlayersApp(StaticLiveServerTestCase):
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

        Args:
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
        This method create a dummy club instance for testing.
        """
        self.club = Club.objects.create(name="Liverpool", logo="test_media/test/club_logo.png", stadium="AN")

    def navigate_to_players(self):
        """
        This method navigates to the players page.
        """
        players_tab = self.driver.find_element(by=By.XPATH, value="//a[@href='/players']")
        players_tab.click()

    def fill_form(self, name, dob, weight, height, club, nationality, position):
        """
        This method fills out the player form.

        Args:
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

        Args:
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
            dob = "1999-10-29",
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
            dob = "1999-10-29",
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
