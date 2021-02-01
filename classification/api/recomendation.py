from django.contrib.auth import get_user_model
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import F, CharField
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from games.models import SwitchGame
from games.api.game import games_all_base_query
from eshop_crawler.settings import (
    VOTE_RECOMENDATION_UPPERBOUND,
    VOTE_RECOMENDATION_LOWERBOUND,
)

from ..models import Recomendation, ConfirmedHighlight, Wishlist
from ..serializers import RecomendationSerializer, recomendation_to_json


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes((IsAuthenticated,))
def recomendation(request, game_code):
    if request.method == 'GET':
        return recomendation_get(request, game_code)

    elif request.method == 'POST':
        return recomendation_post(request, game_code)

    elif request.method == 'DELETE':
        return recomendation_delete(request, game_code)


def recomendation_get(request, game_code):
    game = get_object_or_404(SwitchGame, game_code_unique=game_code)

    try:
        instance = Recomendation.objects.get(user=request.user, game=game)

        return Response(
            {'recomends': instance.recomends},
            status=status.HTTP_200_OK)

    except Recomendation.DoesNotExist:
        return Response(status=status.HTTP_200_OK)


def recomendation_post(request, game_code):
    game = get_object_or_404(SwitchGame, game_code_unique=game_code)

    try:
        instance = Recomendation.objects.get(user=request.user, game=game)
    except Recomendation.DoesNotExist:
        instance = None

    if instance:
        recomendation = RecomendationSerializer(
            instance=instance,
            data=request.data,
            context={'user': request.user, 'game': game})
    else:
        recomendation = RecomendationSerializer(
            data=request.data,
            context={'user': request.user, 'game': game})

    success = recomendation.is_valid()

    if success:
        recomendation.save()
        confirm_highlight_by_vote(game)
        Wishlist.objects.filter(game=game, user=request.user).delete()
        return Response(status=status.HTTP_200_OK)

    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


def recomendation_delete(request, game_code):
    game = get_object_or_404(SwitchGame, game_code_unique=game_code)
    instance = get_object_or_404(Recomendation, user=request.user, game=game)

    instance.delete()
    confirm_highlight_by_vote(game)

    return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def current_user_recomendations(request):
    return user_recomendations(request.user)


@api_view(['GET'])
def username_user_recomendations(request, username):
    user = get_object_or_404(get_user_model(), username=username)
    return user_recomendations(user)


def user_recomendations(user):
    recomendations = recomendation_all_base_query().filter(user=user)

    likes = recomendations \
        .filter(recomends=True) \
        .order_by('-date')[:10]

    dislikes = recomendations \
        .filter(recomends=False) \
        .order_by('-date')[:10]

    response = {}
    response['likes'] = map(
        lambda x: recomendation_to_json(x, user), likes)
    response['dislikes'] = map(
        lambda x: recomendation_to_json(x, user), dislikes)

    return Response(response, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def current_user_all_recomendations(request, recomends):
    return user_all_recomendations(request.user, recomends)


@api_view(['GET'])
def username_user_all_recomendations(request, username, recomends):
    user = get_object_or_404(get_user_model(), username=username)
    return user_all_recomendations(user, recomends)


def user_all_recomendations(user, recomends):
    recomendations = recomendation_all_base_query() \
        .filter(user=user, recomends=(recomends == 'likes')) \
        .order_by('-date')

    response = map(lambda x: recomendation_to_json(x, user), recomendations)
    return Response(response, status=status.HTTP_200_OK)


@api_view(['POST', 'DELETE'])
@permission_classes((IsAuthenticated, IsAdminUser))
def highlight_admin(request, game_id):
    if request.method == 'POST':
        return highlight_admin_post(request, game_id)

    elif request.method == 'DELETE':
        return highlight_admin_delete(request, game_id)


def highlight_admin_post(request, game_id):
    game = get_object_or_404(SwitchGame, id=game_id)

    try:
        ConfirmedHighlight.objects.get(game=game, confirmed_by='STF')
        return Response(status=status.HTTP_400_BAD_REQUEST)

    except ConfirmedHighlight.DoesNotExist:
        pass

    confirmed_highlight = ConfirmedHighlight(game=game, confirmed_by='STF')

    try:
        confirmed_highlight.save()
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        print('Error posting highlight for game {}'.format(game))
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def highlight_admin_delete(request, game_id):
    game = get_object_or_404(SwitchGame, id=game_id)
    confirmed_highlight = get_object_or_404(
        ConfirmedHighlight, game=game, confirmed_by='STF')

    try:
        confirmed_highlight.delete()
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        print('Error deleting highlight for game {}'.format(game))
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def confirm_highlight_by_vote(game):
    likes_count = game.recomendation_set.filter(recomends=True).count()
    dislikes_count = game.recomendation_set.filter(recomends=False).count()

    delta = likes_count - dislikes_count

    # If should add Highlight
    if delta >= VOTE_RECOMENDATION_UPPERBOUND:
        if ConfirmedHighlight.objects \
                .filter(game=game, confirmed_by='VOT').count() == 0:

            confirmed = ConfirmedHighlight(game=game, confirmed_by='VOT')
            confirmed.save()

    # If should delete Highlight
    elif delta <= VOTE_RECOMENDATION_LOWERBOUND:
        if ConfirmedHighlight.objects \
                .filter(game=game, confirmed_by='VOT').count():

            confirmed = ConfirmedHighlight.objects.get(
                game=game, confirmed_by='VOT')
            confirmed.delete()


def recomendation_all_base_query(user=None):
    query = Recomendation.objects \
        .filter(game__hide=False) \
        .annotate(game_title=Coalesce(
            'game__game_eu__title', 'game__game_us__title')) \
        .annotate(game_image=Coalesce(
            'game__game_eu__image_sq_url', 'game__game_us__front_box_art',
            output_field=CharField())) \
        .annotate(game_code=F('game__game_code_unique')) \
        .annotate(release_us=F('game__game_us__release_date')) \
        .annotate(release_eu=F('game__game_eu__release_date')) \
        .annotate(tags=ArrayAgg('game__confirmedtag__tag__name',
                                distinct=True)) \
        .annotate(review_id=F('review__id'))

    return query
