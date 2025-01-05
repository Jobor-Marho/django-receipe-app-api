"""
Test Tags API
"""
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from core.models import Tags, Receipe
from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status
from receipe.serializers import TagSerializer

TAGS_URL =reverse('receipe:tag-list')

def detail_url(tag_id):
    """Create and return a tag detail url"""
    return reverse('receipe:tag-detail', args=[tag_id])


def create_user(**params):
    """Create and return user"""
    return get_user_model().objects.create_user(**params)

def create_tag(user, name):
    """Create and return tag"""

    return Tags.objects.create(user=user, name=name)

class PublicTagsAPITests(TestCase):
    """Test unauthenticated Tags api"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving tags"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateTagsAPITests(TestCase):
    """Test Authenticated API calls for tags API"""

    def setUp(self):
        self.client = APIClient()
        self.user =  create_user(email="test@example.com", password='12345')
        self.client.force_authenticate(self.user)

    def test_get_tags_list(self):
        """Test retrieving list of tags"""
        create_tag(user=self.user, name='tag1')
        create_tag(user=self.user, name='tag2')

        res = self.client.get(TAGS_URL)
        tags = Tags.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_tags_for_a_user(self):
        """Test retrieving tags for an authenticated user"""
        newuser = create_user(email='test1@example.com', name='user2')
        create_tag(newuser, 'newusertag')
        create_tag(self.user, 'usertag1')
        create_tag(self.user, 'usertag2')

        res = self.client.get(TAGS_URL)
        tags = Tags.objects.filter(user=self.user).order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(len(res.data), 2)


    def test_tag_update(self):
        """Test updating a tag"""

        tag = create_tag(self.user, name='newtag')

        update_payload = {
            'name': 'update'
        }

        url = detail_url(tag.id)
        res = self.client.patch(url, update_payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, update_payload['name'])

    def test_delete_tag(self):
        """Test deleting tag"""

        tag = create_tag(self.user, name='newtag')

        url = detail_url(tag.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        tag_exists = Tags.objects.filter(id=tag.id).exists()
        self.assertFalse(tag_exists)

    def test_filter_tags_assigned_to_receipe(self):
        """Test listing tags assigned to receipe"""
        tag1 = create_tag(self.user, name='Breakfast')
        tag2 = create_tag(self.user, name='Lunch')

        receipe = Receipe.objects.create(title="receipe",
                                         price=Decimal(9.89),
                                         time_minutes=34,
                                         user=self.user)
        receipe.tags.add(tag1)

        res = self.client.get(TAGS_URL, {"assigned_only": 1})

        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)

        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filter_tags_unique(self):
        """Test filtered tags returns unique list """
        tag = create_tag(self.user, name='Breakfast')
        create_tag(self.user, name='Dinner')

        receipe1 = Receipe.objects.create(title="receipe",
                                          time_minutes=45,
                                          price=Decimal(4.5),
                                          user=self.user)
        receipe2 = Receipe.objects.create(title="receipe2",
                                          time_minutes=45,
                                          price=Decimal(4.5),
                                          user=self.user)
        receipe1.tags.add(tag)
        receipe2.tags.add(tag)

        res = self.client.get(TAGS_URL, {"assigned_only": 1})
        self.assertEqual(len(res.data), 1)



