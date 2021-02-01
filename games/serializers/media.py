from rest_framework import serializers

from games.models import SwitchGameMedia


class SwitchGameMediaSerializer(serializers.Serializer):
    media_type = serializers.CharField(max_length=3)
    url = serializers.CharField(max_length=256)

    def create(self, validated_data):
        new_media = SwitchGameMedia(
            media_type=validated_data['media_type'],
            url=validated_data['url'],
            game=self.context['game'],
            order=self.context['order'],
        )

        try:
            new_media.save()
        except Exception as e:
            print('Error while adding media for game {}'
                .format(self.context['game']))

        return new_media

    def update(self, instance, validated_data):
        instance.media_type = validated_data['media_type']
        instance.url = validated_data['url']

        try:
            instance.save()
        except Exception as e:
            print('Error while updating media {}'.format(instance.id))

        return instance
