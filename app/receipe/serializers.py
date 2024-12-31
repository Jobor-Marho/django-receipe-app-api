"""
Serializer for receipe APIs
"""

from rest_framework import serializers
from core.models import Receipe, Tags

class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tags"""
    class Meta:
        model = Tags
        fields = ['id', 'name']
        read_only_fields = ['id']

class ReceipeSerializer(serializers.ModelSerializer):
    """Serializer for Receipes"""

    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Receipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link', 'tags']
        read_only_fields = ['id', 'user']


    def update(self, instance, validated_data):
        # Prevent updating the user field directly
        validated_data.pop('user', None)
        return super().update(instance, validated_data)

    def create(self, validated_data):
        """Create receipe"""
        tags = validated_data.pop('tags', [])
        receipe = Receipe.objects.create(**validated_data)
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tags.objects.get_or_create(user=auth_user, **tag)
            receipe.tags.add(tag_obj)

        return receipe

class ReceipeDetailSerializer(ReceipeSerializer):
    """Serializer for receipe detail view"""

    class Meta(ReceipeSerializer.Meta):
        fields = ReceipeSerializer.Meta.fields + ['description']

class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tags"""
    class Meta:
        model = Tags
        fields = ['id', 'name']
        read_only_fields = ['id']
