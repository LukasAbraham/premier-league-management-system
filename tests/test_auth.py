from selenium import webdriver
from django.test import LiveServerTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from django.contrib.auth.models import User
from apps.auth.models import UserProfile

class TestSignUp(LiveServerTestCase):
    databases = ['test']
    def setUp(self):
        options = Options()
        options.add_argument("--headless=new")
        self.driver = webdriver.Chrome(options=options)
        self.driver.get('http://localhost:8000/auth/sign_up/')
        self.driver.maximize_window()

    def tearDown(self):
        # these lines are just for inspection
        print(User.objects.using('test').all())
        print(UserProfile.objects.using('test').all())
        User.objects.using('test').filter(username__startswith='test_user').delete()
        self.driver.quit()

    def fill_form(self, username, password, key):
        username_field = self.driver.find_element(by=By.NAME, value="username")
        password_field = self.driver.find_element(by=By.NAME, value="password1")
        confirm_password_field = self.driver.find_element(by=By.NAME, value="password2")
        key_field = self.driver.find_element(by=By.NAME, value="key")
        submit_button = self.driver.find_element(by=By.XPATH, value="//input[@type='submit']")

        username_field.send_keys(username)
        password_field.send_keys(password)
        confirm_password_field.send_keys(password)
        key_field.send_keys(key)
        submit_button.click()

    def testSignUpWithValidKey(self):
        print("Test sign up with valid key")
        self.fill_form('test_user1', 'test_password1', 'admin')
        WebDriverWait(self.driver, 2).until(EC.presence_of_element_located((By.CLASS_NAME, 'image_insert')))

        try:
            # image_insert is a special and unique element displayed only for admin
            image_insert_button = self.driver.find_element(by=By.CLASS_NAME, value='image_insert')
            assert image_insert_button is not None
        except NoSuchElementException:
            self.fail("Registration as admin failed - unique element for admin not found")
        
    def testSignUpWithInvalidKey(self):
        print("Test sign up with invalid key")
        self.fill_form('test_user2', 'test_password2', 'user')
        
        try:
            image_insert_button = self.driver.find_element(by=By.CLASS_NAME, value='image_insert')
            self.fail("Registration with invalid key succeeded - unique element for admin found")
        except NoSuchElementException:
            pass
        
        
class TestSignIn(LiveServerTestCase):
    def setUp(self):
        options = Options()
        options.add_argument("--headless=new")
        self.driver = webdriver.Chrome(options=options)
        self.driver.get('http://localhost:8000/auth/')
        self.driver.maximize_window()

        # print(User.objects.all())
        # self.user = User.objects.create_user(username='user', password='user123456')
        # self.userProfile = UserProfile.objects.create(user=self.user, type='user')
        # self.admin = User.objects.create_user(username='admin', password='admin123456')
        # self.adminProfile = UserProfile.objects.create(user=self.admin, type='admin')

    def tearDown(self):
        self.driver.quit()
        

    def fill_form(self, username, password):
        username_field = self.driver.find_element(by=By.NAME, value="username")
        password_field = self.driver.find_element(by=By.NAME, value="password")
        submit_button = self.driver.find_element(by=By.XPATH, value="//input[@type='submit']")

        username_field.send_keys(username)
        password_field.send_keys(password)
        submit_button.click()

    def testValidSignIn(self):
        print("Test valid sign in")
        self.fill_form('normal_user', 'user123123')
        self.driver.implicitly_wait(2)
        print(self.driver.title)
        assert self.driver.title == "Home"
        
    def testInvalidSignIn(self):
        print("Test invalid sign in")
        self.fill_form('normal_user', 'abcdef123')
        self.driver.implicitly_wait(2)
        alert = self.driver.find_element(by=By.CLASS_NAME, value="alert")
        print(alert.text)
        assert alert.text == "You did not sign in correctly."
        
    def testSignInWithEmptyUsername(self):
        print("Test sign in with empty username field")
        self.fill_form('normal_user', '')
        self.driver.implicitly_wait(2)
        alert = self.driver.find_element(by=By.CLASS_NAME, value="alert")
        print(alert.text)
        assert alert.text == "You did not sign in correctly."

    def testSignInWithEmptyPassword(self):
        print("Test sign in with empty password field")
        self.fill_form('', 'user123456')
        self.driver.implicitly_wait(2)
        alert = self.driver.find_element(by=By.CLASS_NAME, value="alert")
        print(alert.text)
        assert alert.text == "You did not sign in correctly."
        
    def testSignInAsAdmin(self):
        print("Test sign in as admin")
        self.fill_form('admin', 'admin123123')
        WebDriverWait(self.driver, 2).until(EC.presence_of_element_located((By.CLASS_NAME, 'image_insert')))
        
        try:
            # image_insert is a special and unique element displayed only for admin
            image_insert = self.driver.find_element(by=By.CLASS_NAME, value='image_insert')
            assert image_insert is not None
        except NoSuchElementException:
            self.fail("Sign in as admin failed, cause the unique element for admin didn't show up")
        
    def testSignInAsUser(self):
        print("Test sign in as user")
        self.fill_form('normal_user', 'user123123')
        
        try:
            image_insert = self.driver.find_element(by=By.CLASS_NAME, value='image_insert')
            self.fail("Sign in as normal user failed, unique element for only admin found.")
        except NoSuchElementException:
            pass