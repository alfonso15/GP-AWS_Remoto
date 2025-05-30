from django.test import TestCase
from ..models import User


class UserTest(TestCase):

    def test_create_superuser(self):
        """Create Super User"""
        user = User.objects.create_superuser('super@mail.com', 'Pas5w0rd')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
