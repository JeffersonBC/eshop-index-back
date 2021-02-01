from django.contrib.auth import get_user_model

from rest_framework import serializers

from datetime import datetime
import re

from ..models import SwitchGameUS, SwitchGame


class SwitchGameUSSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=128)
    slug = serializers.SlugField(max_length=128)
    release_date = serializers.CharField(max_length=12)

    nsuid = serializers.CharField(max_length=14, required=False)
    game_code = serializers.CharField(max_length=18)

    front_box_art = serializers.URLField()
    video_link = serializers.CharField(max_length=32, required=False)

    def create(self, validated_data):
        switch_game_us = self.validated_data_to_new(validated_data)

        try:
            switch_game_us.save()
        except Exception as e:
            print('Error while saving us game {} ({})'
                  .format(switch_game_us, e))
            return switch_game_us

        clean_game_code = re.sub(
            r'[\-\. ]+', '',
            validated_data.get('game_code')
        )

        # If Game already in DB, update it with US Game
        if (
            SwitchGame.objects.filter(game_code_unique=clean_game_code[4:9])
                .exists()
        ):
            switch_game = SwitchGame.objects.get(
                game_code_unique=clean_game_code[4:9])
            switch_game.game_us = switch_game_us

        # If Game not yet in DB, add one and assign US Game to it
        else:
            switch_game = SwitchGame(
                game_us=switch_game_us,
                game_code_unique=clean_game_code[4:9]
            )

        try:
            switch_game.save()
        except Exception as e:
            print('Error while saving game {} ({})'.format(switch_game, e))

        return switch_game_us

    def update(self, instance, validated_data):
        release_datetime = datetime.strptime(
            validated_data.get('release_date'), '%b %d, %Y')
        clean_game_code = re.sub(
            r'[a-zA-Z0-9]+', '',
            validated_data.get('game_code', instance.game_code)
        )

        instance.title = validated_data.get('title', instance.title)
        instance.slug = validated_data.get('slug', instance.slug)
        instance.release_date = release_datetime

        instance.nsuid = validated_data.get('nsuid', instance.nsuid)

        instance.game_code_system = clean_game_code[0:3]
        instance.game_code_region = clean_game_code[3:4]
        instance.game_code_unique = clean_game_code[4:9]

        instance.front_box_art = validated_data.get(
            'front_box_art', instance.front_box_art)
        instance.video_link = validated_data.get(
            'video_link', instance.video_link)

        instance.save()
        return instance

    def validated_data_to_new(self, validated_data):
        release_datetime = datetime.strptime(
            validated_data.get('release_date'), '%b %d, %Y')
        clean_game_code = re.sub(
            r'[\-\. ]+', '', validated_data.get('game_code'))

        switch_game_us = SwitchGameUS(
            title=validated_data.get('title'),
            slug=validated_data.get('slug')[0:50],
            release_date=release_datetime,

            nsuid=validated_data.get('nsuid'),

            game_code_system=clean_game_code[0:3],
            game_code_region=clean_game_code[3:4],
            game_code_unique=clean_game_code[4:9],

            front_box_art=validated_data.get('front_box_art'),
            video_link=validated_data.get('video_link'),
        )

        return switch_game_us
