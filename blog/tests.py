from django.test import TestCase, Client, RequestFactory
from django.urls import resolve, reverse
from django.contrib.auth.models import User
from django.http import HttpRequest
from .models import Group, Post, Membership
from django.conf import settings
from django.utils import timezone
from . import views
import unittest

LOGIN_USER_DATA = {'username': 'test',
                   'email': 'test@test.com',
                   'password': 'test123'}
NEW_USER_DATA = {'username': 'new user',
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
CREATE_GROUP_DATA = {'name': 'create new group',
                  'theme': 'GE',

                  }
UPDATE_GROUP_DATA = {'name': 'updated_group',
                  'theme': 'SP',

                  }
NEW_POST_DATA = {'title':'test',
                 'text': 'this is a test text'}
CREATE_POST_DATA = {'title':'create new post',
                 'text': 'this is a test text'}
UPDATE_POST_DATA = {'title': 'update title',
                    'text': 'this is updated text'}
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

    def tearDown(self):
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
        # self.assertEqual(response.content, self.login_error)
        # self.assertInHTML(response, self.login_error)
        self.assertTemplateUsed(response, 'login.html')
        #TODO: fix test, read data from response if possible, choose between render() and HTTPResponse


class RegistrationPageTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.reg_passwords_error = settings.REGISTRATION_PASSWORDS_ERROR_MESSAGE.encode('utf-8')
        self.existing_user = User.objects.create_user(**LOGIN_USER_DATA)
        self.reg_user_exists_error = settings.REGISTRATION_USER_EXISTS_ERROR_MESSAGE.encode('utf-8')

    def tearDown(self):
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
        response = self.client.post('/register/',
                                    data=UNVALID_REGISTRATION_USER_DATA)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, self.reg_passwords_error)

    def test_registration_with_existing_user_credentials(self):
        response = self.client.post('/register/', data=LOGIN_USER_DATA)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, self.reg_user_exists_error)


class GroupTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.anonymous_client = Client()
        self.user = User.objects.create_user(**LOGIN_USER_DATA)
        self.client.login(username='test', password='test123')
        self.new_group = Group.create(**NEW_GROUP_DATA, creator=self.user)


    def tearDown(self):
        del self.client
        del self.anonymous_client
        del self.user
        del self.new_group

    def test_groups_url_resolves_to_GroupsList_view(self):
        found_view = resolve('/groups/')
        self.assertEqual(found_view.url_name, 'group_list')

    def test_groups_page_returns_correct_template(self):
        response = self.client.get('/groups/')
        self.assertTemplateUsed(response, 'groups/groups_list.html')
        self.assertEqual(response.status_code, 200)

    def test_groups_page_redirects_unauthorised_user_to_login_page(self):
        response = self.anonymous_client.get('/groups/')
        self.assertRedirects(response, '/login/?next=/groups/')

    def test_group_info_url_resolves_to_GroupInfo_view(self):
        # import pdb; pdb.set_trace()
        found_view = resolve(f'/groups/{self.new_group.pk}/')
        self.assertEqual(found_view.url_name, 'group_info')

    def test_create_new_group_by_user(self):
        response = self.client.post('/groups/new/', data=CREATE_GROUP_DATA)
        CREATE_GROUP_DATA['creator'] = self.user
        group = Group.objects.get(**CREATE_GROUP_DATA)
        self.assertTrue(group)
        self.assertRedirects(response, '/groups/')

    def test_create_group_page_returns_correct_template(self):
        response = self.client.get("/groups/new/")
        self.assertTemplateUsed(response, 'groups/group_create.html')
        self.assertEqual(response.status_code, 200)

    def test_group_update_url_resolves_to_GroupUpdate_view(self):
        found_view = resolve(f'/groups/{self.new_group.pk}/update/')
        self.assertEqual(found_view.url_name, 'group_update')

    def test_update_group_by_user(self):
        response = self.client.post(f'/groups/{self.new_group.pk}/update/',
                                    data=UPDATE_GROUP_DATA)
        group = Group.objects.get(pk=self.new_group.pk)
        self.assertEqual(group.name, UPDATE_GROUP_DATA['name'])
        self.assertEqual(group.theme, UPDATE_GROUP_DATA['theme'])
        self.assertRedirects(response, f'/groups/{self.new_group.pk}/')

    def test_group_delete_url_resolves_to_GroupDelete_view(self):
        found_view = resolve(f'/groups/{self.new_group.pk}/delete/')
        self.assertEqual(found_view.url_name, 'group_delete')

    def test_delete_group_by_user(self):
        before = Group.objects.count()
        response = self.client.post(f'/groups/{self.new_group.pk}/delete/')
        after = Group.objects.count()
        self.assertRedirects(response, '/groups/')
        self.assertEqual(after, before - 1)

    def test_join_group_by_user(self):
        response = self.client.post(f'/groups/{self.new_group.pk}/')
        self.assertRedirects(response, f'/groups/{self.new_group.pk}/')

    def test_create_private_group(self):
        response = self.client.post('/groups/new/', data={**CREATE_GROUP_DATA,
                                                          'private': 'on'})
        group = Group.objects.get(**CREATE_GROUP_DATA)
        self.assertTrue(group.is_private)

    def test_invite_user_to_private_group(self):
        new_user = User.objects.create(**NEW_USER_DATA)
        data = {**CREATE_GROUP_DATA, 'is_private': True}
        group = Group(**data)
        group.save()
        response = self.client.post(f'/groups/{group.pk}/invite/', data={'invited_user': new_user.username})
        membership = Membership.objects.filter(user=new_user, group=group).exists()
        self.assertTrue(membership)


class PostTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.anonymous_client = Client()
        self.user = User.objects.create_user(**LOGIN_USER_DATA)
        self.client.login(username='test', password='test123')
        self.NOT_CREATOR_ERROR = "Only creator is allowed to update the group"
        self.group = Group.create(**NEW_GROUP_DATA, creator=self.user)
        NEW_POST_DATA['creator'] = self.user
        NEW_POST_DATA['group'] = self.group
        self.post = Post.create(**NEW_POST_DATA)

    def tearDown(self):
        del self.client
        del self.anonymous_client
        del self.user

    def test_posts_url_resolves_to_PostsList_view(self):
        found_view = resolve('/posts/')
        self.assertEqual(found_view.url_name, 'post_list')

    def test_posts_url_returns_correct_template(self):
        response = self.client.get('/posts/')
        self.assertTemplateUsed(response, 'posts/posts_list.html')
        self.assertEqual(response.status_code, 200)

    def test_post_info_url_resolves_to_PostInfo_view(self):
        found_view = resolve(f'/posts/{self.post.pk}')
        self.assertEqual(found_view.url_name, 'post_info')

    def test_post_create_url_resolves_to_PostCreate_view(self):
        found_view = resolve(f'/groups/{self.group.pk}/new_post/')
        self.assertEqual(found_view.url_name, 'post_create')

    def test_create_post_by_authenticated_user(self):
        before = Post.objects.count()
        CREATE_POST_DATA['creator'] = self.user
        CREATE_POST_DATA['group'] = self.group
        data = CREATE_POST_DATA
        response = self.client.post(f'/groups/{self.group.pk}/')

        response = self.client.post(f'/groups/{self.group.pk}/new_post/',
                                    data={**CREATE_POST_DATA, 'publish': 'on'})
        after = Post.objects.count()
        post = Post.objects.get(**CREATE_POST_DATA)
        self.assertRedirects(response, '/posts/')
        self.assertEqual(after, before + 1)
        self.assertTrue(post)

    def test_post_update_url_resolves_to_PostUpdate_view(self):
        found_view = resolve(f'/posts/{self.post.pk}/update/')
        self.assertEqual(found_view.url_name, 'post_update')

    def test_update_post_by_authenticated_user(self):
        response = self.client.post(f'/posts/{self.post.pk}/update/',
                                    data=UPDATE_POST_DATA)
        post = Post.objects.get(pk=self.post.pk)
        self.assertEqual(post.text, UPDATE_POST_DATA['text'])
        self.assertEqual(post.title, UPDATE_POST_DATA['title'])
        self.assertRedirects(response, f'/posts/{self.post.pk}')

    def test_update_post_not_by_creator(self):
        user = User.objects.create_user(**NEW_USER_DATA)
        client = Client()
        client.login(username='new user', password='test123')
        response = client.post(f'/posts/{self.post.pk}/update/', data=UPDATE_POST_DATA)
        error = response.context[-1]['error']
        self.assertEqual(error, self.NOT_CREATOR_ERROR)


    def test_post_delete_url_resolves_to_PostDelete_view(self):
        found_view = resolve(f'/posts/{self.post.pk}/delete/')
        self.assertEqual(found_view.url_name, 'post_delete')

    def test_delete_post_by_authenticated_user(self):
        before = Post.objects.count()
        response = self.client.post(f'/posts/{self.post.pk}/delete/')
        after = Post.objects.count()
        post = Post.objects.filter(pk=self.post.pk).exists()
        self.assertEqual(after, before - 1)
        self.assertFalse(post)
        self.assertRedirects(response, '/posts/')

    def test_anonymous_user_not_allowed_to_create_post(self):
        response = self.anonymous_client.post(f'/groups/{self.group.pk}/new_post/',
                             data=CREATE_POST_DATA)
        self.assertRedirects(response, '/login/?next=/groups/1/new_post/')


class DraftTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.anonymous_client = Client()
        self.user = User.objects.create_user(**LOGIN_USER_DATA)
        self.client.login(username='test', password='test123')
        self.group = Group.create(**NEW_GROUP_DATA, creator=self.user)
        NEW_POST_DATA['creator'] = self.user
        NEW_POST_DATA['group'] = self.group
        self.post = Post.create(**NEW_POST_DATA)

    def tearDown(self):
        del self.client
        del self.anonymous_client
        del self.user

    def test_drafts_url_resolves_to_DraftsList_view(self):
        found_view = resolve('/drafts/')
        self.assertEqual(found_view.url_name, 'drafts_list')

    def test_drafts_url_returns_correct_template(self):
        response = self.client.get('/drafts/')
        self.assertTemplateUsed(response, 'posts/drafts_list.html')

    def test_drafts_url_returned_correct_list_of_drafts(self):
        draft = Post.objects.create(**NEW_POST_DATA)
        response = self.client.get('/drafts/')
        for draft in response.context[-1]['drafts']:
            self.assertIsNone(draft['date_created'])

    def test_publish_draft_by_user(self):
        draft = Post.objects.create(**NEW_POST_DATA)
        response = self.client.post(f'/posts/{draft.pk}/publish/')
        posted = Post.objects.get(pk=draft.pk)
        self.assertIsNotNone(posted.date_created)
        self.assertRedirects(response, '/drafts/')
