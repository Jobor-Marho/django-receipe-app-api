"""
Test for ingredients API
"""
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from receipe.serializers import IngredientSerializer
from core.models import Ingredient, Receipe


INGREDIENTS_URL = reverse("receipe:ingredient-list")


def detail_url(ingredient_id):
    """Create and return ingredient detail link"""
    return reverse("receipe:ingredient-detail", args=[ingredient_id])

def create_user(**params):
    """Create and return user"""
    return get_user_model().objects.create_user(**params)

def create_ingredients(**params):
    """Create and return ingredients"""
    return Ingredient.objects.create(**params)


class PublicIngredientAPITest(TestCase):
    """Test for unauthorized user making requests to ingredient API"""

    def setUp(self):
        """Initialized the setup by creating an API connection"""
        self.client = APIClient()


    def test_getting_ingredient_api_for_unauthorized_user(self):
        """Test for ensuring requests are'nt availble for an unauthorized user"""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateIngredientAPITest(TestCase):
    """Test for authenticated users using the Ingredients API"""

    def setUp(self):
        self.user = create_user(email="test@example.com", password="123456")
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieving_list_of_ingredients(self):
        """Test getting all ingredients list for a user"""
        payload = {"name": "ingrdients 1", "user": self.user}

        ingredient = create_ingredients(**payload)

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertTrue(len(ingredients), 1)


    def test_get_ingredients_for_a_user(self):
        """Test retrieving ingredients for an authenticated user"""

        newuser = create_user(email='test1@example.com', name='user2')
        payload = {"name": "ingrdients 1", "user": self.user}
        create_ingredients(**payload)


        res = self.client.get(INGREDIENTS_URL)
        ingredients = Ingredient.objects.filter(user=self.user).order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(len(res.data), 1)


    def test_ingredient_update(self):
        """Test updating an ingredient"""

        payload = {"name": "newingredient", "user": self.user}

        ingredient = create_ingredients(**payload)

        update_payload = {
            'name': 'update'
        }

        url = detail_url(ingredient.id)
        res = self.client.patch(url, update_payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, update_payload['name'])

    def test_delete_ingredient(self):
        """Test deleting Ingredient"""
        payload = {"name": "ingredient 1", "user": self.user}
        ingredient = create_ingredients(**payload)

        url = detail_url(ingredient.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        ingredient_exists = Ingredient.objects.filter(id=ingredient.id).exists()
        self.assertFalse(ingredient_exists)

    def test_filter_ingredients_assigned_to_receipe(self):
        """Test listing ingredients assigned to receipe"""
        payload = {"name": "peper", "user": self.user}
        ingredient1 = create_ingredients(**payload)
        payload = {"name": "onion", "user": self.user}
        ingredient2 = create_ingredients(**payload)
        receipe = Receipe.objects.create(title="Porridge",
                                         time_minutes=12,
                                         price=Decimal(4.56),
                                         user=self.user)
        receipe.ingredients.add(ingredient1)

        res = self.client.get(INGREDIENTS_URL, {"assigned_only": 1})
        
        s1 = IngredientSerializer(ingredient1)
        s2 = IngredientSerializer(ingredient2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_ingredients_unique(self):
        """Test filtered ingredients return a unique list"""
        payload = {"name": "peper", "user": self.user}
        ingredient1 = create_ingredients(**payload)
        payload = {"name": "brocolli", "user": self.user}
        create_ingredients(**payload)

        r1 = Receipe.objects.create(title="eggs",
                                    time_minutes=23,
                                    price=Decimal(34.44),
                                    user=self.user)
        r2 = Receipe.objects.create(title="Herb eggs",
                                    time_minutes=23,
                                    price=Decimal(34.44),
                                    user=self.user)
        r1.ingredients.add(ingredient1)
        r2.ingredients.add(ingredient1)

        res = self.client.get(INGREDIENTS_URL, {"assigned_only": 1})

        self.assertEqual(len(res.data), 1)