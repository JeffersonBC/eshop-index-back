from datetime import datetime

from django.contrib.auth import get_user_model

from rest_framework import serializers

from ..models import SwitchGameEU, SwitchGame


class SwitchGameEUSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=256)
    url = serializers.CharField(max_length=256)
    date_from = serializers.CharField(max_length=20)
    excerpt = serializers.CharField(max_length=9999, allow_blank=True)

    nsuid_txt = serializers.ListField(required=False)
    product_code_txt = serializers.ListField()
    fs_id = serializers.CharField(max_length=8)

    gift_finder_carousel_image_url_s = serializers.CharField(max_length=256)
    gift_finder_detail_page_image_url_s = serializers.CharField(max_length=256)
    gift_finder_wishlist_image_url_s = serializers.CharField(max_length=256)

    image_url = serializers.CharField(max_length=256)
    image_url_sq_s = serializers.CharField(max_length=256)
    image_url_h2x1_s = serializers.CharField(max_length=256)

    def create(self, validated_data):
        switch_game_eu = self.validated_data_to_new(validated_data)

        try:
            switch_game_eu.save()
        except Exception as e:
            print('Error while saving eu game {} ({})'.format(switch_game_eu, e))
            return switch_game_eu

        # If Game already in DB, update it with EU Game
        if SwitchGame.objects.filter(
            game_code_unique=validated_data.get('product_code_txt')[0].strip()[4:9]
        ).exists():
            switch_game = SwitchGame.objects.get(
                game_code_unique=validated_data.get('product_code_txt')[0].strip()[4:9])
            switch_game.game_eu = switch_game_eu

        # If Game not yet in DB, add one and assign EU Game to it
        else:
            switch_game = SwitchGame(
                game_eu=switch_game_eu,
                game_code_unique=validated_data.get('product_code_txt')[0].strip()[4:9]
            )

        try:
            switch_game.save()
        except Exception as e:
            print('Error while saving game {} ({})'.format(switch_game, e))

        return switch_game_eu

    def update(self, instance, validated_data):
        release_datetime = datetime.strptime(
            validated_data.get('date_from')[:10], '%Y-%M-%d')
        nsuid = (
            validated_data.get('nsuid_txt')[0]
            if validated_data.get('nsuid_txt') is not None
            else None
        )

        instance.title = validated_data.get('title', instance.title)
        instance.url = validated_data.get('url', instance.url)
        instance.release_date = release_datetime
        instance.description = validated_data.get(
            'excerpt', instance.description),

        instance.nsuid = nsuid
        instance.game_code = validated_data.get(
            'product_code_txt', instance.game_code)
        instance.fs_id = validated_data.get('fs_id', instance.fs_id)

        instance.image_carousel_url = validated_data.get(
            'gift_finder_carousel_image_url_s',
            instance.image_carousel_url
        )
        instance.image_detail_page_url = validated_data.get(
            'gift_finder_detail_page_image_url_s',
            instance.image_detail_page_url
        )
        instance.image_wishlist_url = validated_data.get(
            'gift_finder_wishlist_image_url_s',
            instance.image_wishlist_url
        )

        instance.image_url = validated_data.get(
            'image_url', instance.image_url)
        instance.image_sq_url = validated_data.get(
            'image_url_sq_s', instance.image_sq_url)

        instance.save()
        return instance

    def validated_data_to_new(self, validated_data):
        release_datetime = datetime.strptime(
            validated_data.get('date_from')[:10], '%Y-%m-%d')

        nsuid = (
            validated_data.get('nsuid_txt')[0]
            if validated_data.get('nsuid_txt') is not None
            else None
        )

        switch_game_eu = SwitchGameEU(
            title=validated_data.get('title'),
            url=validated_data.get('url'),
            release_date=release_datetime,
            description=validated_data.get('excerpt'),

            nsuid=nsuid,
            fs_id=validated_data.get('fs_id'),

            game_code_system=validated_data.get('product_code_txt')[0][0:3],
            game_code_region=validated_data.get('product_code_txt')[0][3:4],
            game_code_unique=validated_data.get('product_code_txt')[0].strip()[4:9],

            image_carousel_url=validated_data.get(
                'gift_finder_carousel_image_url_s'),
            image_detail_page_url=validated_data.get(
                'gift_finder_detail_page_image_url_s'),
            image_wishlist_url=validated_data.get(
                'gift_finder_wishlist_image_url_s'),

            image_url=validated_data.get('image_url'),
            image_sq_url=validated_data.get('image_url_sq_s'),
            image_sq_h2_url=validated_data.get('image_url_h2x1_s'),
        )

        return switch_game_eu
