from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from loginapp.forms import *

class IndexTests(TestCase):
    """To test index page"""
    def test_index_renders(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)


class SignUpTest(TestCase):
    """Form test"""

    def register_test_forms(self):
        """User registeration testing"""
        form_data = {'username': 'testuser',
            'email': 'testemail@test.com',
            'password1': '1234',
            'password2': '1234'}
        form = RegistrationForm(form_data)
        self.assertTrue(form.is_valid())

    def setUp(self):
    	"""Setup for logging in"""
        self.credentials = {'username': 'testuser',
            'password': '1234'}
        User.objects.create_user(**self.credentials)

    def test_login(self):
        # send login data
        response = self.client.post('/user/accounts/login/', self.credentials, follow=True)
        # should be logged in now
        self.assertTrue(response.context['user'].is_active)
