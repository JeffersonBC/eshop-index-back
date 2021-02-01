from django.contrib.auth import get_user_model
from django.db.models import Count, Q, F
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from games.models import SwitchGame
from classification.api.recomendation import confirm_highlight_by_vote
from classification.models import Review, VoteReview
from classification.serializers import (
    ReviewSerializer,
    VoteReviewSerializer,
    review_to_json,
)


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes((IsAuthenticated,))
def review(request, game_code):
    if request.method == 'GET':
        return review_get(request, game_code)

    if request.method == 'POST':
        return review_post(request, game_code)

    if request.method == 'DELETE':
        return review_delete(request, game_code)


def review_get(request, game_code):
    game = get_object_or_404(SwitchGame, game_code_unique=game_code)

    try:
        instance = Review.objects.get(user=request.user, game=game)

        return Response(
            {'review_text': instance.review_text},
            status=status.HTTP_200_OK)

    except Review.DoesNotExist:
        return Response(status=status.HTTP_200_OK)


def review_post(request, game_code):
    game = get_object_or_404(SwitchGame, game_code_unique=game_code)

    try:
        instance = Review.objects.get(user=request.user, game=game)
        review = ReviewSerializer(
            instance=instance,
            data=request.data,
            context={'user': request.user, 'game': game})

    except Review.DoesNotExist:
        review = ReviewSerializer(
            data=request.data,
            context={'user': request.user, 'game': game})

    success = review.is_valid()

    if success:
        review.save()
        confirm_highlight_by_vote(game)
        return Response(status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


def review_delete(request, game_code):
    game = get_object_or_404(SwitchGame, game_code_unique=game_code)
    instance = get_object_or_404(Review, user=request.user, game=game)

    instance.delete()
    confirm_highlight_by_vote(game)

    return Response(status=status.HTTP_200_OK)


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes((IsAuthenticated,))
def review_vote(request, review_id):
    if request.method == 'GET':
        return review_vote_get(request, review_id)

    if request.method == 'POST':
        return review_vote_post(request, review_id)

    if request.method == 'DELETE':
        return review_vote_delete(request, review_id)


def review_vote_get(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    try:
        instance = VoteReview.objects.get(user=request.user, review=review)
        return Response({'vote': instance.vote}, status=status.HTTP_200_OK)

    except VoteReview.DoesNotExist:
        return Response(status=status.HTTP_200_OK)


def review_vote_post(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    try:
        instance = VoteReview.objects.get(user=request.user, review=review)
        vote = VoteReviewSerializer(
            instance=instance,
            data=request.data,
            context={'user': request.user, 'review': review})

    except VoteReview.DoesNotExist:
        vote = VoteReviewSerializer(
            data=request.data,
            context={'user': request.user, 'review': review})

    success = vote.is_valid()

    if success:
        vote.save()
        return Response(status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


def review_vote_delete(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    instance = get_object_or_404(VoteReview, user=request.user, review=review)
    instance.delete()

    return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
def all_reviews(request, game_code):
    quantity = request.query_params.get('qtd', None)
    offset = request.query_params.get('offset', 0)

    if quantity:
        quantity = int(quantity)

    reviews = []

    reviews_query = Review.objects \
        .filter(game__game_code_unique=game_code) \
        .annotate(useful=Count('votereview',
                               filter=Q(votereview__vote__exact=True))) \
        .annotate(not_useful=Count('votereview',
                                   filter=Q(votereview__vote__exact=False))) \
        .annotate(vote_sum=F('useful') - F('not_useful')) \
        .order_by(
            '-vote_sum', '-last_update_date'
        )[offset: offset + quantity if quantity else None]

    for review in reviews_query:
        reviews.append(review_to_json(review, request.user))

    return Response(reviews, status=status.HTTP_200_OK)
