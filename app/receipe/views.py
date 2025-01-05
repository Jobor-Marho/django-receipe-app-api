"""
Views for the receipeAPI
"""
from drf_spectacular.utils import (extend_schema_view, extend_schema, OpenApiParameter, OpenApiTypes)
from rest_framework import (viewsets, mixins, status)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from core.models import Receipe, Tags, Ingredient
from receipe import serializers


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                "tags",
                OpenApiTypes.STR,
                description="Comma separated list of tag IDs to filter"
            ),
            OpenApiParameter(
                "ingredients",
                OpenApiTypes.STR,
                description="Comma separated list of ingredient IDs to filter"
            )
        ]
    )
)
class ReceipeViewSet(viewsets.ModelViewSet):
    """View for managing receipe """

    serializer_class = serializers.ReceipeDetailSerializer
    queryset = Receipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _params_to_ints(self, qs):
        """Convert a list of strings to integers"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        """Retrieve receipes for authenticated user"""
        tags = self.request.query_params.get("tags")
        ingredients = self.request.query_params.get("ingredients")
        queryset = self.queryset

        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)
        if  ingredients:
            ingr_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingr_ids)

        return queryset.filter(
            user=self.request.user
        ).order_by("-id").distinct()


    def get_serializer_class(self):
        """Return the serializer class for request"""
        if self.action == "list":
            return serializers.ReceipeSerializer
        elif self.action == "upload_image":
            return serializers.ReceipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new Receipe"""
        serializer.save(user=self.request.user)

    @action(methods=["POST"], detail=True, url_path="upload-image")
    def upload_image(self, request, pk=None):
        """Upload an image to Receipe"""
        receipe = self.get_object()
        serializer = self.get_serializer(receipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_200_OK)

        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)



    def list(self, request, *args, **kwargs):
        """List for all receipes"""

        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({'detail': 'No recipe found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'detail': 'Recipe deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)



@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                "assigned_only",
                OpenApiTypes.INT,
                enum=[0, 1],
                description="Filter by items assigned to receipes"
            )
        ]
    )
)
class BaseReceipeAttrViewSet(mixins.DestroyModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.ListModelMixin,
                 viewsets.GenericViewSet):
    """Base ViewSet for Receipe attributes"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        f"""Get {self.queryset.model.__name__.lower()}s for authenticated user """
        assigned_only = bool(
            int(self.request.query_params.get("assigned_only", 0))
        )
        queryset = self.queryset
        if assigned_only:
           queryset = queryset.filter(receipe__isnull=False)
        return queryset.filter(
            user=self.request.user
            ).order_by('-name').distinct()

    def list(self, request, *args, **kwargs):
        f"""List for all {self.queryset.model.__name__.lower()}s"""
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({'detail': f'No {self.queryset.model.__name__.lower()} found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    def destroy(self, request, *args, **kwargs):
        """Custom message for delete operation."""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {'detail': f'{self.queryset.model.__name__} deleted successfully.'},
            status=status.HTTP_204_NO_CONTENT
        )

class TagViewSet(BaseReceipeAttrViewSet):
    """View for managing Tags"""

    serializer_class = serializers.TagSerializer
    queryset = Tags.objects.all()


class IngredientsViewSet(BaseReceipeAttrViewSet):
    """Manage Ingredients in the Database"""
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()

