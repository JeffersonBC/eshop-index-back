from rest_framework import serializers

from ..models import TagGroup


class TagGroupSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=64)
    allow_vote = serializers.BooleanField()
    min_games_for_search = serializers.IntegerField()

    def create(self, validated_data):
        tag_group = TagGroup(
            name=validated_data['name'],
            allow_vote=validated_data['allow_vote'],
            min_games_for_search=validated_data['min_games_for_search'])

        tag_group.save()

        return tag_group

    def update(self, instance, validated_data):
        instance.name = validated_data['name']
        instance.allow_vote = validated_data['allow_vote']
        instance.min_games_for_search = validated_data['min_games_for_search']

        instance.save()

        return instance
