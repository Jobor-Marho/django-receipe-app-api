"""
Views for the receipeAPI
"""

from rest_framework import (viewsets, mixins)
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from core.models import Receipe, Tags, Ingredient
from receipe import serializers

class ReceipeViewSet(viewsets.ModelViewSet):
    """View for managing receipe """

    serializer_class = serializers.ReceipeDetailSerializer
    queryset = Receipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve receipes for authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-id')



    def get_serializer_class(self):
        """Return the serializer class for request"""
        if self.action == "list":
            return serializers.ReceipeSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new Receipe"""
        serializer.save(user=self.request.user)



    def list(self, request, *args, **kwargs):
        """List for all receipes"""

        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({'detail': 'No recipe found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class BaseReceipeAttrViewSet(mixins.DestroyModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.ListModelMixin,
                 viewsets.GenericViewSet):
    """Base ViewSet for Receipe attributes"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        f"""Get {self.queryset.model.__name__.lower()}s for authenticated user """
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def list(self, request, *args, **kwargs):
        f"""List for all {self.queryset.model.__name__.lower()}s"""
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({'detail': f'No {self.queryset.model.__name__.lower()} found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class TagViewSet(BaseReceipeAttrViewSet):
    """View for managing Tags"""

    serializer_class = serializers.TagSerializer
    queryset = Tags.objects.all()


class IngredientsViewSet(BaseReceipeAttrViewSet):
    """Manage Ingredients in the Database"""
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()

