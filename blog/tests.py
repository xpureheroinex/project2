from django.test import TestCase, Client, RequestFactory
from django.urls import resolve, reverse
from django.contrib.auth.models import User
from django.http import HttpRequest
from .models import Group
from django.conf import settings
from django.utils import timezone
from . import views
import unittest

LOGIN_USER_DATA = {'username': 'test',
             'email': 'test@test.com',
                   'password': 'test123'}

REGISTRATION_USER_DATA = {'username': 'test1',
             'email': 'test@test.com',
             'password1': 'test123',
             'password2': 'test123'}

UNVALID_REGISTRATION_USER_DATA = {'username': 'test2',
             'email': 'test@test.com',
             'password1': 'test123',
             'password2': 'wrongpassword'}

NEW_GROUP_DATA = {'name': 'test_group',
                  'theme': 'GE',
                  }
# Create your tests here.
class HomePageTest(TestCase):

    def test_root_url_resolves_to_home_page_view(self):
        found_view = resolve('/')
        self.assertEqual(found_view.func, views.home_page)

    def test_home_page_returns_correct_template(self):
        client = Client()
        response = client.get('/')
        self.assertTemplateUsed(response, 'homepage.html')
        self.assertEqual(response.status_code, 200)


class LoginPageTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(**LOGIN_USER_DATA)
        self.login_error = settings.LOGIN_ERROR_MESSAGE.encode('utf-8')

    def TearDown(self):
        del self.client
        del self.user
        del self.login_error

    def test_login_url_resolves_to_user_login_view(self):
        found_view = resolve('/login/')
        self.assertEqual(found_view.func, views.user_login)

    def test_login_page_returns_correct_template(self):
        response = self.client.get('/login/')
        self.assertTemplateUsed(response, 'login.html')
        self.assertEqual(response.status_code, 200)

    def test_login_is_successful(self):
        response = self.client.post('/login/', {'username': self.user.username,
                                               'password': 'test123'})
        # import pdb; pdb.set_trace()
        self.assertRedirects(response, '/')

    def test_login_with_wrong_password(self):
        response = self.client.post('/login/', {'username': self.user.username,
                                                'password': 'wrongpass'})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.content, self.login_error)


class RegistrationPageTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.reg_passwords_error = settings.REGISTRATION_PASSWORDS_ERROR_MESSAGE.encode('utf-8')
        self.existing_user = User.objects.create_user(**LOGIN_USER_DATA)
        self.reg_user_exists_error = settings.REGISTRATION_USER_EXISTS_ERROR_MESSAGE.encode('utf-8')

    def TearDown(self):
        del self.client
        del self.existing_user

    def test_register_url_resolves_to_user_registration_view(self):
        found_view = resolve('/register/')
        self.assertEqual(found_view.func, views.user_registration)

    def test_registration_page_returns_correct_template(self):
        response = self.client.get('/register/')
        self.assertTemplateUsed(response, 'registration.html')
        self.assertEqual(response.status_code, 200)

    def test_registration_is_successful(self):
        response = self.client.post('/register/', data=REGISTRATION_USER_DATA)
        self.assertRedirects(response, '/')

    def test_registration_with_different_passwords(self):
        response = self.client.post('/register/', data=UNVALID_REGISTRATION_USER_DATA)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, self.reg_passwords_error)

    def test_registration_with_existing_user_credentials(self):
        response = self.client.post('/register/', data=LOGIN_USER_DATA)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, self.reg_user_exists_error)


class GroupTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.new_user = User.objects.create_user(**LOGIN_USER_DATA)
        self.request_factory = RequestFactory()
        # import pdb; pdb.set_trace()
        self.user = User.objects.create_user(**LOGIN_USER_DATA)

    def test_groups_url_resolves_to_GroupsList_view(self):
        found_view = resolve('/groups/')
        self.assertEqual(found_view.url_name, 'group_list')

    def test_groups_page_returns_correct_template(self):
        response = self.client.get('/groups/')
        self.assertTemplateUsed(response, 'groups/groups_list.html')
        self.assertEqual(response.status_code, 200)

    def test_create_new_group_by_user(self):
        # request = self.request_factory.post('/groups/new/', data=NEW_GROUP_DATA)
        # # import pdb; pdb.set_trace()
        # request.user = self.user
        # response = views.GroupCreate(request)

        user = self.user
        client = self.client
        client.login(username=user.username, password=user.password)
        response = client.post('/groups/new/', data=NEW_GROUP_DATA)
        self.assertRedirects(response, '/groups/')

