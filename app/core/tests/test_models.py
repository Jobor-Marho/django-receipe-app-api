"""
Test for models
"""

from django.test import TestCase #for making tests involving the database (alias of it)
from unittest.mock import patch #for testing image uploading mechanism
from django.contrib.auth import get_user_model
from decimal import Decimal
from core import models

def create_user(**params):
    """Create and return a valid user instance"""
    return get_user_model().objects.create_user(**params)

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
        """Test creating a superuser"""
        user = get_user_model().objects.create_superuser(email='test@example.com', password='test123')

        self.assertEqual(user.is_superuser, True)
        self.assertEqual(user.is_staff, True)

    def test_create_receipe(self):
        """Test creating a receipe is successful"""
        user = get_user_model().objects.create_user(
            email='test@example.com',
            password='test123'
            )
        receipe = models.Receipe.objects.create(
            user=user,
            title='sample name',
            time_minutes=5,
            price=Decimal('5.50'),
            description='sample descrip'
        )
        self.assertEqual(str(receipe), receipe.title)

    def test_create_tag(self):
        """Test create a tag is succeful"""
        user = create_user(email='new@exmaple.com', password='12345')
        tag = models.Tags.objects.create(user=user, name='Tag 1')
        self.assertEqual(str(tag), tag.name)

    def test_create_ingredients(self):
        """Test creating a new Ingredients"""
        ingredient = models.Ingredient.objects.create(name="new ingredient", user=get_user_model().objects.create_user(email="testuser@example.com", password="123456"))
        self.assertEqual(str(ingredient), ingredient.name)

    @patch('core.models.uuid.uuid4')
    def test_receipe_file_name_uuid(self, patched_mock_uuid):
        """Test generating image path"""
        uuid = 'test_uuid'
        patched_mock_uuid.return_value = uuid
        file_path = models.receipe_image_file_path(None, 'example.jpg')

        self.assertEqual(file_path, f'uploads/receipe/{uuid}.jpg')






