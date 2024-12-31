"""Urls mappings for receipe app"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from receipe import views


app_name = 'receipe'


router = DefaultRouter()
router.register('receipes', views.ReceipeViewSet)
router.register('receipe-tags', views.TagViewSet, basename='tag')


urlpatterns = [
    path('', include(router.urls)),
]