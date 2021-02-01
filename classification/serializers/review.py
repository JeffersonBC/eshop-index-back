from django.contrib.auth.models import AnonymousUser
from rest_framework import serializers

from ..models import Review, Recomendation, VoteReview
from games.models import SwitchGame


class ReviewSerializer(serializers.Serializer):
    review_text = serializers.CharField(max_length=1000, required=False)
    recomends = serializers.BooleanField()

    def create(self, validated_data):
        try:
            recomendation = Recomendation.objects.get(
                game=self.context['game'],
                user=self.context['user'])

        except Recomendation.DoesNotExist:
            recomendation = Recomendation(
                game=self.context['game'],
                user=self.context['user'],
                recomends=validated_data['recomends'])

        try:
            recomendation.save()
        except Exception as e:
            print('Error while creating review for game {} ({})'
                  .format(self.context['game'], e))

        new_review = Review(
            game=self.context['game'],
            user=self.context['user'],
            review_text=validated_data['review_text'],
            recomendation=recomendation)

        try:
            new_review.save()
        except Exception as e:
            print('Error while creating review for game {} ({})'
                  .format(self.context['game'], e))
            recomendation.delete()

        return new_review

    def update(self, instance, validated_data):
        try:
            recomendation = Recomendation.objects.get(
                game=self.context['game'],
                user=self.context['user'])

            recomendation.recomends = validated_data['recomends']
            recomendation.save()

        except Recomendation.DoesNotExist:
            recomendation = Recomendation(
                game=self.context['game'],
                user=self.context['user'],
                recomends=validated_data['recomends'])

            recomendation.save()
            instance.recomendation = recomendation

        instance.review_text = validated_data['review_text']
        instance.has_edited = True
        instance.save()

        return instance


def review_to_json(review, user, simple_version=False):
    if type(user) == AnonymousUser:
        user = None

    try:
        vote = VoteReview.objects.get(user=user, review=review)
    except VoteReview.DoesNotExist:
        vote = None

    review_json = {
        'id': review.id,
        'review_text': review.review_text,
        'useful': review.votereview_set.filter(vote=True).count(),
        'not_useful': review.votereview_set.filter(vote=False).count(),
        'date': review.last_update_date,
        'has_edited': review.has_edited,
        'vote': vote.vote if vote else None,
    }

    if not simple_version:
        review_json['recomends'] = review.recomendation.recomends
        review_json['user'] = review.user.username

    return review_json
