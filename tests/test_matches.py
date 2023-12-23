import os
from time import sleep
from datetime import datetime
from django.utils import timezone
from django.core.files import File
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from apps.clubs.models import Club
from apps.auth.models import UserProfile
from apps.players.models import Player
from apps.matches.models import Match, Result, GoalEvent
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException


class TestMatchesApp(StaticLiveServerTestCase):
    """
    This class contains automation tests for the Matches app.
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
        self.driver.implicitly_wait(5)
        self.admin = User.objects.create_user(username='admin', password='admin123456')
        self.admin_profile = UserProfile.objects.create(user=self.admin, type='admin')
        self.login('admin', 'admin123456')
        # add dummy clubs for testing
        self.club1 = self.create_club("Liverpool", "test_media/test_club_logo.png", "AN")
        self.club2 = self.create_club("Manchester City", "test_media/test_club_logo.png", "ET")
        self.navigate_to_matches()

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

    def create_club(self, name, logo_path, stadium):
        """
        This method creates a dummy club for testing

        Parameters:
            name (str): The club name
            logo_path (str): The path to club logo image
            stadium (str): The club's stadium

        Returns:
            Club instance: A valid club instance with the input information
        """
        with open(logo_path, 'rb') as f:
            logo_image = File(f)
            return Club.objects.create(
                name=name, 
                logo=logo_image,
                stadium=stadium,
                status="V",
            )

    def navigate_to_matches(self):
        """
        This method navigates to the matches page.
        """
        matches_tab = self.driver.find_element(by=By.XPATH, value="//a[@href='/matches']")
        matches_tab.click()

    def fill_match_form(self, round, time, club1, club2):
        """
        This method fills out the match form.

        Parameters:
            round (int): Fixture round number
            time (datetime): Match fixture
            club1 (str): Club 1 name (indicate the club which competes its opponent at home)
            club2 (str): Club 2 name
        """
        try: 
            round_field = self.driver.find_element(by=By.ID, value="id_round")
            time_field = self.driver.find_element(by=By.ID, value="id_time")
            club1_field = self.driver.find_element(by=By.ID, value="id_club1")
            club2_field = self.driver.find_element(by=By.ID, value="id_club2")
            save_button = self.driver.find_element(by=By.XPATH, value="//button[@class='btn btn-primary w-100']")
        except NoSuchElementException as e:
            self.fail(f"Element not found: {e}")
        
        round_field.clear()
        round_field.send_keys(round)
        # add custom time (currently not working)
        # date = datetime.strptime(time, "%d/%m/%Y %H:%M:%S")
        # self.driver.execute_script("arguments[0].value = arguments[1];", time_field, date.strftime("%Y-%m-%dT%H:%M"))
        club1_select = Select(club1_field)
        club2_select = Select(club2_field)
        club1_select.select_by_visible_text(club1)
        club2_select.select_by_visible_text(club2)
        save_button.click()
        
    def fill_result_form(self, club1_goals, club2_goals):
        """
        This method fills out the result form of a previous match.

        Parameters:
            club1_goals (int): number of goals scored by club 1
            club2_goals (int): number of goals scored by club 2
        """
        club1_goals_field = self.driver.find_element(by=By.ID, value="id_club1_goals")
        club1_goals_field.send_keys(club1_goals)
        club2_goals_field = self.driver.find_element(by=By.ID, value="id_club2_goals")
        club2_goals_field.send_keys(club2_goals)
        save_button = self.driver.find_element(by=By.XPATH, value="//button[@class='btn btn-primary w-100']")
        save_button.click()
        
    def fill_goal_event_form(self, id, scoring_player_name, assisting_player_name, type, time, club):
        """
        This method fills out the goal event forms for a previous match. 

        Parameters:
            id (int): the number order of the goal event form in the formset.
            scoring_player_name (str): name of the scoring player for that goal event
            assisting_player_name (str): name of the assisting player for that goal event (can be None)
            type (str): type of the scored goal (can be None), there are 3 goal types: Normal, Free Kick and Own goal
            time (_type_): time in which the goal event happened
            club (_type_): the name of a club which scored this goal event.
        """
        scoring_player_field = self.driver.find_element(by=By.ID, value=f"id_form-{id}-scoring_player")
        scoring_player_select = Select(scoring_player_field)
        scoring_player_select.select_by_visible_text(scoring_player_name)
        if assisting_player_name:
            assisting_player_field = self.driver.find_element(by=By.ID, value=f"id_form-{id}-assisting_player")
            assisting_player_select = Select(assisting_player_field)
            assisting_player_select.select_by_visible_text(assisting_player_name)
        if type:
            type_field = self.driver.find_element(by=By.ID, value=f"id_form-{id}-type")
            type_select = Select(type_field)
            type_select.select_by_visible_text(type)
        time_field = self.driver.find_element(by=By.ID, value=f"id_form-{id}-time")
        time_field.send_keys(time)
        club_field = self.driver.find_element(by=By.ID, value=f"id_form-{id}-club")
        club_select = Select(club_field)
        club_select.select_by_visible_text(club)
            
    def add_match(self, round, time, club1, club2):
        """
        This method adds a new match through the UI

        Parameters:
            round (int): Fixture round number
            time (str): Match fixture
            club1 (str): Club 1 name
            club2 (str): Club 2 name
        """
        add_match_button = self.driver.find_element(by=By.XPATH, value="//button[text()='Add']")
        add_match_button.click()
        self.fill_match_form(round, time, club1, club2)

    def test_add_match(self):
        """
        This method tests the addition of a new match
        """
        self.add_match(1, "12/12/2018 10:13:20", "Liverpool", "Manchester City")
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".alert.alert-success")))
            success_message = self.driver.find_element(by=By.CSS_SELECTOR, value=".alert.alert-success")
        except (TimeoutException, NoSuchElementException) as e:
            self.fail(f"Test failed: {e}")  
        self.assertEqual(success_message.text, 'Match was created successfully!', "The success message was not displayed")
        
        match = Match.objects.get(round=1)
        self.assertIsNotNone(match, "An added match was not found")

    def test_update_match(self):
        """
        This method tests the updating of a match's result and goal event(s)
        """
        self.match = Match.objects.create(
            round=2,
            time=datetime.strptime("2022-10-29 10:30:00", "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc),
            club1=self.club1,
            club2=self.club2,
        )
        Player.objects.create(
            name="John Doe",
            dob = "1998-02-03",
            weight=80,
            height=180,
            club=self.club1,
            nationality="Croatian",
            position="FW"
        )
        Player.objects.create(
            name="Jane Doe",
            dob = "2000-11-28",
            weight=70,
            height=175,
            club=self.club2,
            nationality="English",
            position="MF"
        )
        self.driver.refresh()
        try:
            update_button = self.driver.find_element(by=By.ID, value=f"update-{self.match.id}")
        except NoSuchElementException as e:
            self.fail(f"Test failed: {e}")
        update_button.click()
        # add result
        self.fill_result_form(1, 1)
        # add goal event 1
        self.fill_goal_event_form(0, "John Doe", None, None, 69, "Liverpool")
        # add goal event 2
        self.fill_goal_event_form(1, "Jane Doe", None, None, 81, "Manchester City")
        save_button = self.driver.find_element(by=By.XPATH, value="//button[@class='btn btn-primary w-100']")
        save_button.click()
        assert self.driver.title == "Matches", "The system didn't navigate back to the matches page"
        updated_match = Match.objects.get(id=self.match.id)
        assert updated_match.result.club1_goals == 1 and updated_match.result.club2_goals == 1, "The updated result is not correct"

        updated_match_goal_events = list(GoalEvent.objects.filter(match=self.match))
        assert updated_match_goal_events[0].scoring_player.name == "John Doe" and updated_match_goal_events[1].scoring_player.name == "Jane Doe", "The goal events are updated incorrectly"
        

    def test_edit_match(self):
        """
        This method tests the editing of a match
        """
        self.match = Match.objects.create(
            round=2,
            time=datetime.strptime("2015-10-29 10:30:00", "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc),
            club1=self.club1,
            club2=self.club2,
        )
        self.driver.refresh()
        try:
            edit_button = self.driver.find_element(by=By.ID, value=f"edit-{self.match.id}")
        except NoSuchElementException as e:
            self.fail(f"Test failed: {e}")
        edit_button.click()
        self.fill_match_form(3, "12/12/2018 10:13:20", "Manchester City", "Liverpool")  
        updated_match = Match.objects.get(id=self.match.id)
        assert updated_match.round == 3 and updated_match.club1.name == "Manchester City" and updated_match.club2.name == "Liverpool", "The match was not updated correctly"
        
    def test_delete_match(self):
        """
        This method tests the deletion of a match
        """
        self.match = Match.objects.create(
            round=2,
            time=datetime.strptime("2015-10-29 10:30:00", "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc),
            club1=self.club1,
            club2=self.club2,
        )
        self.driver.refresh()
        try:
            delete_button = self.driver.find_element(by=By.ID, value=f"delete-{self.match.id}")
        except NoSuchElementException as e:
            self.fail(f"Test failed: {e}")
        delete_button.click()

        alert = self.driver.switch_to.alert
        alert.accept()
        # add a little delay for the db to update
        sleep(2)
        with self.assertRaises(Match.DoesNotExist):
            Match.objects.get(id=self.match.id)