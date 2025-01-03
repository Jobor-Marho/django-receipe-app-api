"""
Serializer for receipe APIs
"""

from rest_framework import serializers
from core.models import Receipe, Tags, Ingredient


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for Ingredient"""
    class Meta:
        model = Ingredient
        fields = ["id", "name"]
        read_only_fields = ['id']

class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tags"""
    class Meta:
        model = Tags
        fields = ["id", "name"]
        read_only_fields = ['id']


class ReceipeSerializer(serializers.ModelSerializer):
    """Serializer for Receipes"""

    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Receipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link', 'tags', 'ingredients']
        read_only_fields = ['id', 'user']

    def _get_or_create_tags(self, tags, receipe):
        """Handle getting or creating tags as needed"""

        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tags.objects.get_or_create(user=auth_user, **tag)
            receipe.tags.add(tag_obj)

    def _get_or_create_ingredients(self, ingredients, receipe):
        """Handle getting or creating ingrdients"""

        auth_user = self.context['request'].user
        for ingr in ingredients:
            ingr_obj, created = Ingredient.objects.get_or_create(user=auth_user, **ingr)
            receipe.ingredients.add(ingr_obj)

    def create(self, validated_data):
        """Create receipe"""
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])
        receipe = Receipe.objects.create(**validated_data)
        self._get_or_create_tags(tags=tags, receipe=receipe)
        self._get_or_create_ingredients(ingredients=ingredients, receipe=receipe)
        return receipe

    def update(self, instance, validated_data):
        """Update receipe"""
        tags = validated_data.pop("tags", None)
        ingredients = validated_data.pop("ingredients", None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)
        elif ingredients is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredients(ingredients, instance)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

class ReceipeDetailSerializer(ReceipeSerializer):
    """Serializer for receipe detail view"""

    class Meta(ReceipeSerializer.Meta):
        fields = ReceipeSerializer.Meta.fields + ['description', 'image']

class ReceipeImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images"""

    class Meta:
        model = Receipe
        fields = ["id", "image"]
        read_only_field = ["id"]
        extra_kwargs = {"image": {"required": "True"}}


