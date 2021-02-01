import json

from rest_framework import serializers

from games.models import SwitchGameListSlot, SwitchGameList


class SwitchGameListSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=128)
    query_json = serializers.CharField(max_length=256)
    frequency = serializers.FloatField()

    def create(self, validated_data):
        query_parsed_json = json.loads(validated_data['query_json'])
        is_logged_list = query_parsed_json['unrated_only'] \
            if 'unrated_only' in query_parsed_json else False

        new_list = SwitchGameList(
            title=validated_data['title'],
            query_json=validated_data['query_json'],
            logged_list=is_logged_list,
            frequency=validated_data['frequency'],
            slot=self.context['slot'],
        )

        try:
            new_list.save()
        except Exception as e:
            print('Error while creating list for slot {}'
                .format(self.context['slot'].id))

        return new_list

    def update(self, instance, validated_data):
        query_parsed_json = json.loads(validated_data['query_json'])
        is_logged_list = query_parsed_json['unrated_only'] \
            if 'unrated_only' in query_parsed_json else False

        instance.title = validated_data['title']
        instance.query_json = validated_data['query_json']
        instance.frequency = validated_data['frequency']
        instance.logged_list = is_logged_list

        try:
            instance.save()
        except Exception as e:
            print('Error while updating list {} for slot {}'
                .format(instance.id, self.context['slot'].id))

        return instance
