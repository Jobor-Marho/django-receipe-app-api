"""
Test for Receipe APIs
"""

from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from core.models import Receipe, Tags, Ingredient
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from receipe.serializers import ReceipeSerializer, ReceipeDetailSerializer

RECEIPES_URL = reverse('receipe:receipe-list')

def detail_url(receipe_id):
    """Create and return a receipe detail url"""
    return reverse('receipe:receipe-detail', args=[receipe_id])

def create_receipe(user, **params):
    """Create and return a sample receipe"""
    defaults = {
        'title': 'sample title',
        'time_minutes': 22,
        'price': Decimal(5.25),
        'description': 'test description',
        'link': 'https://testexample.com'
    }
    defaults.update(params)

    receipe = Receipe.objects.create(user=user, **defaults)
    return receipe

def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)


class PublicReceipeAPITests(TestCase):
    """Test unauthenticated receipe requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """test for checking a user is authorized to call the API"""
        res = self.client.get(RECEIPES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateReceipeAPITests(TestCase):
    """Test authenticated receipe requests"""

    def setUp(self):
        self.user = create_user(email='test@example.com', password='1234')
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_receipe(self):
        """Test retrieving the list of receipe"""
        create_receipe(user=self.user)
        create_receipe(user=self.user)

        res = self.client.get(RECEIPES_URL)
        receipes = Receipe.objects.all().order_by('-id')
        serializer = ReceipeSerializer(receipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


    def test_retrieve_receipe_limited_to_a_user(self):
        """Test retrieving the list of receipe for a user"""
        other_user = create_user(email='otheruser@example.com', password='12345')
        create_receipe(user=other_user)
        create_receipe(user=self.user)
        res = self.client.get(RECEIPES_URL)
        receipes = Receipe.objects.filter(user=self.user).order_by('-id')
        serializer = ReceipeSerializer(receipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_receipe_detail(self):
        """Test get receipe detail"""
        receipe = create_receipe(self.user)
        url = detail_url(receipe.id)
        res = self.client.get(url)

        serializer = ReceipeDetailSerializer(receipe)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_receipe(self):
        """Test creating a new Receipe"""
        receipe_payload = {
            'title': 'sample title',
            'time_minutes': 22,
            'price': Decimal(5.25),
            'description': 'test description',
            'link': 'https://testexample.com',

        }

        res = self.client.post(RECEIPES_URL, receipe_payload)
        receipe = Receipe.objects.get(id=res.data['id'])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(receipe.user, self.user)


    def test_partial_update(self):
        """test partial update of a receipe"""
        original_link = 'https://originalexample.com'
        receipe = create_receipe(
            user=self.user,
            title='sample title',
            link=original_link
        )

        payload = {'title': 'New receipe title'}
        url = detail_url(receipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        receipe.refresh_from_db()
        self.assertEqual(receipe.title, payload['title'])
        self.assertEqual(receipe.link, original_link)
        self.assertEqual(receipe.user, self.user)

    def test_full_update(self):
        """Test full update of receipe"""
        receipe = create_receipe(
            user=self.user,
            title='sample title',
            link='https://original_link.com',
            time_minutes=9,
            price= Decimal(10.00)
        )
        updated_payload = {
            'title': 'updated title',
            'link': 'https://new-link.com',
            'time_minutes': 0,
            'price': Decimal(5.00)
        }
        url = detail_url(receipe.id)

        res = self.client.put(url, updated_payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        receipe.refresh_from_db()

        #loop through the data to see if the values are correctly updated
        for k,v in updated_payload.items():
            self.assertEqual(getattr(receipe, k), v)
        self.assertEqual(receipe.user, self.user)

    def test_delete_receipe(self):
        """Test deleting a receipe"""
        receipe = create_receipe(self.user)
        url = detail_url(receipe.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        # check if the receipe objects still exists
        exists = Receipe.objects.filter(id=receipe.id).exists()

        self.assertFalse(exists)

    def test_update_user_returns_error(self):
        """Test updating the receipe user results in error"""

        new_user = create_user(email='new@email.com', password='123456')
        receipe = create_receipe(self.user)

        payload = {'user': new_user.id}
        url = detail_url(receipe.id)
        res = self.client.patch(url, payload)
        receipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(receipe.user, self.user)

    def test_delete_other_users_receipe_error(self):
        """Self trying to delete other user api"""
        new_user = create_user(email='user2@gmail.com', password='775444')
        receipe = create_receipe(user=new_user)

        url = detail_url(receipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Receipe.objects.filter(id=receipe.id).exists())

    def test_create_receipe_with_new_tags(self):
        """Test creating a receipe with new Tags"""

        payload = {
            "title": "new title",
            "time_minutes": "30",
            "price": Decimal(250),
            "tags": [
                {
                    "name": "Thai"
                },
                {
                    "name": "Dinner"
                }
            ]
        }

        res = self.client.post(RECEIPES_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        receipes = Receipe.objects.filter(user=self.user).order_by("-id")
        self.assertEqual(receipes.count(), 1)
        receipe = receipes[0]
        self.assertEqual(receipe.tags.count(), 2)
        for tag in payload["tags"]:
            exists = receipe.tags.filter(
                name=tag["name"],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_receipe_with_existing_tags(self):
        """Create a receipe with existing tags"""
        new_tag = Tags.objects.create(user=self.user, name="Indian")

        payload = {
            "title": "New Receipe",
            "time_minutes": 60,
            "price": Decimal(4.45),
            "tags": [{"name": "Indian"}, {"name": "Russian"}]
        }

        res = self.client.post(RECEIPES_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        receipes = Receipe.objects.filter(user=self.user)
        self.assertEqual(receipes.count(), 1)
        receipe = receipes[0]
        self.assertEqual(receipe.tags.count(), 2)
        self.assertIn(new_tag, receipe.tags.all())
        for tag in payload["tags"]:
            exists = receipe.tags.filter(
                name=tag["name"],
                user=self.user,
            ).exists()
            self.assertTrue(exists)


    def test_create_tags_on_update(self):
        """Test updating a receipe with an existing or new tags"""
        receipe = create_receipe(self.user)
        payload = {"tags": [{"name": "lunch"}]}
        url = detail_url(receipe.id)
        res = self.client.patch(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tags.objects.get(user=self.user, name="lunch")
        self.assertIn(new_tag, receipe.tags.all())

    def test_update_receipe_assign_tags(self):
        """Test assinging an existing tag when updating receipe"""
        tag_breakfast = Tags.objects.create(user=self.user, name="Breakfast")
        receipe = create_receipe(self.user)
        receipe.tags.add(tag_breakfast)

        tag_lunch = Tags.objects.create(user=self.user, name="Lunch")
        payload = {
            "tags": [{"name": "Lunch"}]
        }

        url = detail_url(receipe.id)
        res = self.client.patch(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, receipe.tags.all())
        self.assertNotIn(tag_breakfast, receipe.tags.all())

    def test_clear_receipe_tags(self):
        """Test clearing tags for a receipe"""
        tag = Tags.objects.create(user=self.user, name='New tag')
        receipe = create_receipe(self.user)
        payload = {"tags": []}
        url = detail_url(receipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(receipe.tags.count(), 0)

    def test_create_receipe_with_new_ingredient(self):
        """Test create a new receipe with ingredient"""
        payload = {
            "title": "New Receipe",
            "time_minutes": 34,
            "price": Decimal(67.53),
            "ingredients": [{"name": "newIngredient"}, {"name": "newingredient2"}]
        }

        res = self.client.post(RECEIPES_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        receipes =  Receipe.objects.filter(user=self.user)
        self.assertEqual(receipes.count(), 1)
        receipe = receipes[0]
        self.assertEqual(receipe.ingredients.count(), 2)
        for ingredients in payload['ingredients']:
            exists = receipe.ingredients.filter(
                name=ingredients["name"],
                user=self.user).exists()
            self.assertTrue(exists)

    def test_create_receipe_with_existing_ingredient(self):
        """test creating receipe with existing ingredients"""
        ingredient = Ingredient.objects.create(user=self.user, name="Ingredient")
        payload = {
            "title": "New receipe",
            "time_minutes": 56,
            "price": Decimal(9.77),
            "ingredients": [{"name": "Ingredient"}, {"name": "newIngredient"}]
        }

        res = self.client.post(RECEIPES_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        receipes = Receipe.objects.filter(user=self.user)
        self.assertEqual(receipes.count(), 1)
        receipe = receipes[0]
        self.assertEqual(receipe.ingredients.count(), 2)
        self.assertIn(ingredient, receipe.ingredients.all())
        for ingredient in payload["ingredients"]:
            exists = receipe.ingredients.filter(
                name=ingredient['name'],
                user=self.user).exists()
            self.assertTrue(exists)

    def test_create_ingredients_on_update(self):
        """Test creating a new no existent ingredient on update"""
        receipe = create_receipe(self.user)
        payload = {"ingredients": [{"name": "lemon"}]}

        url = detail_url(receipe.id)
        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_ingr = Ingredient.objects.get(name="lemon", user=self.user)
        self.assertIn(new_ingr, receipe.ingredients.all())

    def test_update_receipe_assign_ingredients(self):
        """Test assigning an existing ingredients when updating a receipe"""
        ingr1 = Ingredient.objects.create(name="ingr1", user=self.user)
        receipe = create_receipe(self.user)
        receipe.ingredients.add(ingr1)

        ingr2 = Ingredient.objects.create(name="ingr2", user=self.user)

        payload = {"ingredients": [{"name": "ingr2"}]}

        url = detail_url(receipe.id)
        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(ingr2, receipe.ingredients.all())
        self.assertNotIn(ingr1, receipe.ingredients.all())

    def test_clear_receipe_ingredients(self):
        """Test clearing a receipe ingredients"""
        ingredient = Ingredient.objects.create(user=self.user, name="chili")
        receipe = create_receipe(self.user)

        receipe.ingredients.add(ingredient)

        payload = {"ingredients": []}
        url = detail_url(receipe.id)

        res = self.client.patch(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(receipe.ingredients.count(), 0)
