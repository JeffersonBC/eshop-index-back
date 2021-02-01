from rest_framework import serializers

from ..models import VoteReview


class VoteReviewSerializer(serializers.Serializer):
    vote = serializers.BooleanField()

    def create(self, validated_data):
        new_vote = VoteReview(
            review=self.context['review'],
            user=self.context['user'],
            vote=validated_data['vote'])

        try:
            new_vote.save()
        except Exception as e:
            print('Error while voting for review {}'
                  .format(self.context['review'], e))

        return new_vote

    def update(self, instance, validated_data):
        instance.vote = validated_data['vote']
        instance.save()

        return instance
