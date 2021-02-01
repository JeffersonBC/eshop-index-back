from rest_framework import serializers

from ..models import TagGroup, Tag


class TagSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=64)

    def create(self, validated_data):
        tag = Tag(
            name=validated_data['name'],
            tag_group=self.context['tag_group'],
        )
        tag.save()

        return tag

    def update(self, instance, validated_data):
        instance.name = validated_data['name']
        instance.tag_group = self.context['tag_group']
        instance.save()

        return instance
