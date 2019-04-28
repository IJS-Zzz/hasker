from django.conf import settings
from django.test import TestCase, Client
from django.urls import reverse

from ..models import User
from ..views import SingUpView


class TestSingUpView(TestCase):
    def setUp(self):
        self.url = reverse('account:singup')
        self.user_data = {'username': 'test_user',
                          'email': 'test1@example.com',
                          'password1': 'TopSecret9602',
                          'password2': 'TopSecret9602',}

    def test_user_registration_all_fields(self):
        users = User.objects.all()
        self.assertEqual(len(users), 0)

        response = self.client.post(self.url, data=self.user_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response._headers['location'][1],
                         SingUpView.success_url)

        users = User.objects.all()
        self.assertEqual(len(users), 1)
        user = users[0]

        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.username, self.user_data['username'])

    def test_redirect_authenticated_user(self):
        user = User.objects.create(
            username="test1",
            email="test1@example.com",
            password="secret"
        )
        self.client.force_login(user)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response._headers['location'][1],
                         SingUpView.success_url)

    def test_user_email_is_unique(self):
        response = self.client.post(self.url, data=self.user_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response._headers['location'][1],
                         SingUpView.success_url)

        other_user_data = {
            'username': 'other_' + self.user_data['username'],
            'email': self.user_data['email'],
            'password1': 'secret' + self.user_data['password1'],
            'password2': 'secret' + self.user_data['password2'],
        }

        response = self.client.post(self.url, data=self.user_data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue('email' in response.context['form'].errors)
        self.assertContains(response, 'email address already exists')


class TestUserEditView(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="test1",
            email="test1@example.com",
            password="secret"
        )
        self.url = reverse('account:edit')

    def test_unauthorized_user_redirect_to_login_page(self):
        response = self.client.get(self.url)
        redirect_url = settings.LOGIN_URL + '?next=' + self.url

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response._headers['location'][1],
                         redirect_url)

    def test_authorized_user_get_info_about_him(self):
        self.client.force_login(self.user)

        response = self.client.get(self.url)
        ctx = response.context
        self.assertEqual(ctx['form']['email'].value(), self.user.email)


class TestUserProfileView(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="test1",
            email="test1@example.com",
            password="secret"
        )
        self.other_user = User.objects.create(
            username='test2',
            email='test2@example.com',
            password='secret'
        )

    def test_unauthorized_user_can_get_page_registered_user(self):
        response = self.client.get(reverse(
            'account:profile',
            kwargs={'username': self.user.username}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['profile'], self.user)

    def test_authorized_user_can_get_page_other_user(self):
        self.client.force_login(self.other_user)
        response = self.client.get(reverse(
            'account:profile',
            kwargs={'username': self.user.username}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['profile'], self.user)
