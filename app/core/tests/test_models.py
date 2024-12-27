"""
Test for models
"""

from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    """ Test Models"""

    def test_create_user_with_email_successful(self):
        '''Test creating a user with an email is successful'''
        email = 'test@example.com'
        password = 'test123'
        user = get_user_model().objects.create_user(email=email, password=password)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email normalized"""

        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@example.com', 'TEST3@example.com'],
            ['test4@example.com', 'test4@example.com'],
            ['teSt5@exAMpLe.cOm', 'teSt5@example.com']
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a value error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_super_user(self):
        '''Test creating a superuser'''
        user = get_user_model().objects.create_superuser(email='test@example.com', password='test123')

        self.assertEqual(user.is_superuser, True)
        self.assertEqual(user.is_staff, True)
