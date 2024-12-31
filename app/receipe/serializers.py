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
        ref_name = 'TagMain'

class ReceipeSerializer(serializers.ModelSerializer):
    """Serializer for Receipes"""

    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Receipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link', 'tags']
        read_only_fields = ['id', 'user']

    def _get_or_create_tags(self, tags, receipe):
        """Handle getting or creating tags as needed"""

        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tags.objects.get_or_create(user=auth_user, **tag)
            receipe.tags.add(tag_obj)




    def create(self, validated_data):
        """Create receipe"""
        tags = validated_data.pop('tags', [])
        receipe = Receipe.objects.create(**validated_data)
        self._get_or_create_tags(tags=tags, receipe=receipe)
        return receipe

    def update(self, instance, validated_data):
        """Update receipe"""
        tags = validated_data.pop("tags", None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

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
