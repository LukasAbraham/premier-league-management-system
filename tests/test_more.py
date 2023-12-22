import os
import time
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User
from apps.auth.models import UserProfile
from apps.more.models import Regulation
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

class TestRegulation(StaticLiveServerTestCase):
    """
    This class contains automation tests for Regulation sub-screen inside the More app
    """
    def setUp(self):
        """
        This method sets up the test environment before each test method.
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
        self.navigate_to_more()

    def tearDown(self):
        """
        This method cleans up after each test method
        """
        self.driver.quit()
        
    def login(self, username, password):
        """
        This method logs in to the application as an admin

        Args:
            username (str): The username to sign in with
            password (str): The password to sign in with
        """
        username_field = self.driver.find_element(by=By.NAME, value="username")
        password_field = self.driver.find_element(by=By.NAME, value="password")
        submit_button = self.driver.find_element(by=By.XPATH, value="//input[@type='submit']")
        username_field.send_keys(username)
        password_field.send_keys(password)
        submit_button.click()
    
    def navigate_to_more(self):
        """
        This method navigates to the more app
        """
        more_tab = self.driver.find_element(by=By.XPATH, value="//a[@href='/more']")
        more_tab.click()
    
    def fill_regulation_form(self, **kwargs):
        """
        This method fills out the edit regulation form
        """
        for key, value in kwargs.items():
            if value is not None:
                requested_field = self.driver.find_element(by=By.ID, value=f"id_{key}")
                requested_field.clear()
                requested_field.send_keys(value)
        save_button = self.driver.find_element(by=By.XPATH, value="//input[@class='btn btn-primary']")
        save_button.click()
        
    def test_edit_regulation(self):
        """
        This method test the editing of a regulation
        """
        Regulation.objects.create()
        try:
            regulation_block = self.driver.find_element(by=By.ID, value="regulation")
        except NoSuchElementException as e:
            self.fail(f"Test failed: {e}")
        regulation_block.click()
        try:
            edit_button = self.driver.find_element(by=By.XPATH, value="//button[@class='btn btn-primary']")
        except NoSuchElementException as e:
            self.fail(f"Test failed: {e}")
        edit_button.click()
        
        self.fill_regulation_form(**{
            "player_max_age": 90,
            "duration": 120,
        })
        
        edited_regulation = Regulation.objects.get(pk=1)
        assert edited_regulation.player_max_age == 90 and edited_regulation.duration == 120, "The regulation was not updated correctly"

class TestReport(StaticLiveServerTestCase):
    """
    This class contains automation tests for the Report sub-screen inside the More app
    """
    def setUp(self):
        """
        This method sets up the test environment before each test method.
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
        self.navigate_to_more()

    def tearDown(self):
        """
        This method cleans up after each test method
        """
        self.driver.quit()
        
    def login(self, username, password):
        """
        This method logs in to the application as an admin
        
        Parameters:
            username (str): The username to sign in with
            password (str): The password to sign in with
        """
        username_field = self.driver.find_element(by=By.NAME, value="username")
        password_field = self.driver.find_element(by=By.NAME, value="password")
        submit_button = self.driver.find_element(by=By.XPATH, value="//input[@type='submit']")
        username_field.send_keys(username)
        password_field.send_keys(password)
        submit_button.click()
    
    def navigate_to_more(self):
        """
        This method navigates to the more page
        """
        more_tab = self.driver.find_element(by=By.XPATH, value="//a[@href='/more']")
        more_tab.click()
    
    def test_export_report(self):
        """
        This method tests the exporting of a league report
        """
        try:
            report_block = self.driver.find_element(by=By.ID, value="report")
        except NoSuchElementException as e:
            self.fail(f"Test failed: {e}")
        report_block.click()
        try:
            export_button = self.driver.find_element(by=By.XPATH, value="//button[@class='btn btn-primary']")
        except NoSuchElementException as e:
            self.fail(f"Test failed: {e}")
        export_button.click()
        
        # wait for the download to finish
        time.sleep(5) # adjust this if needed
        # adjust your default download path directory
        file_path = 'C:/Users/LENOVO/Downloads/pl_report.pdf'
        if not os.path.exists(file_path):
            self.fail("The expected file was not downloaded")
    