from rest_framework import serializers

from classification.models import Recomendation, Review
from classification.serializers.review import review_to_json


class RecomendationSerializer(serializers.Serializer):
    recomends = serializers.BooleanField()

    def create(self, validated_data):
        new_recomendation = Recomendation(
            game=self.context['game'],
            user=self.context['user'],
            recomends=validated_data['recomends'],
        )

        try:
            new_recomendation.save()
        except Exception as e:
            print('Error while creating recomendation for game {} ({})'
                  .format(self.context['game'], e))

        return new_recomendation

    def update(self, instance, validated_data):
        instance.recomends = validated_data['recomends']
        instance.save()

        return instance


def recomendation_to_json(recomendation, user):

    game_json = {
        'title': recomendation.game_title,
        'game_code': recomendation.game_code,
        'game_image': recomendation.game_image,
        'release_us': recomendation.release_us,
        'release_eu': recomendation.release_eu,
        'tags': recomendation.tags
    }

    response = {'game': game_json}

    try:
        review = Review.objects.get(id=recomendation.review_id)
        response['review'] = review_to_json(review, user)
    except Review.DoesNotExist:
        pass

    return response
