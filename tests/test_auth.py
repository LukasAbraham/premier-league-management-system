from selenium import webdriver
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from django.contrib.auth.models import User
from apps.auth.models import UserProfile

class TestSignUp(StaticLiveServerTestCase):
    """
    This class contains automation tests for sign up functionality
    """
    def setUp(self):
        """
        This method sets up the test environment. It is run before each test method.
        """
        options = Options()
        options.add_argument("--headless=new")
        self.driver = webdriver.Chrome(options=options)
        self.driver.get(f"{self.live_server_url}/auth/sign_up")
        self.driver.maximize_window()

    def tearDown(self):
        """
        This method cleans up after each test method.
        """
        self.driver.quit()

    def fill_form(self, username, password1, password2, key):
        """
        This method fills out the sign in form

        Parameters:
            username (str): The username
            password1 (str): The password
            password2 (str): The confirm password
            key (str): The admin key
        """
        username_field = self.driver.find_element(by=By.NAME, value="username")
        password_field = self.driver.find_element(by=By.NAME, value="password1")
        confirm_password_field = self.driver.find_element(by=By.NAME, value="password2")
        key_field = self.driver.find_element(by=By.NAME, value="key")
        submit_button = self.driver.find_element(by=By.XPATH, value="//input[@type='submit']")

        username_field.send_keys(username)
        password_field.send_keys(password1)
        confirm_password_field.send_keys(password2)
        key_field.send_keys(key)
        submit_button.click()

    def check_failure_alert(self):
        """
        This method checks if there are a failure alert for signing up
        """
        alert = self.driver.find_element(by=By.CLASS_NAME, value="alert")
        assert alert.text == "Account creation failed!"

    def test_signup_with_valid_key(self):
        """
        This method tests signing up with valid admin key
        """
        self.fill_form('test_user1', 'test_password1', 'test_password1', 'admin')
        WebDriverWait(self.driver, 2).until(EC.presence_of_element_located((By.CLASS_NAME, 'image_insert')))

        try:
            # image_insert is a special and unique element displayed only for admin
            image_insert_button = self.driver.find_element(by=By.CLASS_NAME, value='image_insert')
            assert image_insert_button is not None
        except NoSuchElementException:
            self.fail("Registration as admin failed - unique element for admin not found")
        
    def test_signup_with_invalid_key(self):
        """
        This method tests signing up with invalid admin key
        """
        self.fill_form('test_user2', 'test_password2', 'test_password2', 'user')
        assert self.driver.title == "Home"
        try:
            image_insert_button = self.driver.find_element(by=By.CLASS_NAME, value='image_insert')
            self.fail("Registration with invalid key succeeded - unique element for admin found")
        except NoSuchElementException:
            pass
        
    def test_signup_with_mismatched_passwords(self):
        """
        This method tests signing up when the confirm password and password don't match
        """
        self.fill_form('test_user3', 'test_password3', 'test_password4', 'admin')
        self.check_failure_alert()
        
    def test_signup_with_invalid_username(self):
        """
        This method tests signing up with invalid username
        """
        self.fill_form('/////', 'random_password', 'random_password', 'admin')
        self.check_failure_alert()     

    def test_signup_with_invalid_password(self):
        """
        This method tests signing up with invalid password
        """
        self.fill_form('test_user4', '123456', '123456', 'admin')
        self.check_failure_alert()
        
class TestSignIn(StaticLiveServerTestCase):
    """
    This class contains automation tests for the sign in functionality
    """
    def setUp(self):
        """
        This method sets up the test environment. It is run before each test method.
        """
        options = Options()
        options.add_argument("--headless=new")
        self.driver = webdriver.Chrome(options=options)
        self.driver.get(f"{self.live_server_url}/auth")
        self.driver.maximize_window()
        self.driver.implicitly_wait(5)

        self.user = User.objects.create_user(username='user', password='user123456')
        self.userProfile = UserProfile.objects.create(user=self.user, type='user')
        self.admin = User.objects.create_user(username='admin', password='admin123456')
        self.adminProfile = UserProfile.objects.create(user=self.admin, type='admin')

    def tearDown(self):
        """
        This method cleans up after each test method.
        """
        self.driver.quit()
        
    def fill_form(self, username, password):
        """
        This method fills out the sign in form

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

    def check_failure_alert(self):
        """
        This method checks if there are a failure alert for signing in
        """
        alert = self.driver.find_element(by=By.CLASS_NAME, value="alert")
        assert alert.text == "You did not sign in correctly."

    def test_valid_sign_in(self):
        """
        This method tests signing in with valid credentials
        """
        self.fill_form('user', 'user123456')
        assert self.driver.title == "Home"
        
    def test_invalid_sign_in(self):
        """
        This method tests signing in with invalid credentials
        """
        self.fill_form('user', 'abcdef123')
        self.check_failure_alert()
        
    def test_sign_in_with_empty_username(self):
        """
        This method tests signing in with an empty username field.
        """
        self.fill_form('', 'user123456')
        self.check_failure_alert()

    def test_sign_in_with_empty_password(self):
        """
        This method tests signing in with an empty password field.
        """
        self.fill_form('user', '')
        self.check_failure_alert()
        
    def test_sign_in_as_admin(self):
        """
        This method tests signing in as an admin
        """
        self.fill_form('admin', 'admin123456')
        try:
            # image_insert is a special and unique element displayed only for admin
            image_insert = self.driver.find_element(by=By.CLASS_NAME, value='image_insert')
            assert image_insert is not None
        except NoSuchElementException:
            self.fail("Sign in as admin failed, cause the unique element for admin didn't show up")
        
    def test_sign_in_as_user(self):
        """
        This method tests signing in as a user
        """
        self.fill_form('user', 'user123456')
        assert self.driver.title == "Home"
        try:
            image_insert = self.driver.find_element(by=By.CLASS_NAME, value='image_insert')
            self.fail("Sign in as normal user failed, unique element for only admin found.")
        except NoSuchElementException:
            pass