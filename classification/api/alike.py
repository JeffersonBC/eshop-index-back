from django.db.models import Count, Q, OuterRef, Exists, CharField
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from classification.models import ConfirmedAlike, SuggestAlike
from games.models import SwitchGame
from games.api.game import game_to_json, games_all_base_query
from eshop_crawler.settings import VOTE_ALIKE_UPPERBOUND, VOTE_ALIKE_LOWERBOUND


@api_view(['GET'])
def all_confirmed_alike(request, game_code):
    country = request.query_params.get('country', 'US')

    game = get_object_or_404(SwitchGame, game_code_unique=game_code)

    alike_query = game.alike_game1 \
        .filter(game1=game) \
        .values('game2_id')

    games_ids = map(lambda x: x['game2_id'], alike_query)

    games_query = games_all_base_query(request.user, country) \
        .filter(id__in=games_ids) \
        .annotate(votes=Count('suggested_alike_game2',
                              filter=Q(suggested_alike_game2__game1=game))) \
        .order_by('-votes', 'game_title')

    games_list = []
    for game in games_query:
        # If game already in games_list list, skip it
        if len(games_list) and \
                games_list[-1]['game_code'] == game.game_code_unique:
            continue

        games_list.append(game_to_json(game, request.user))

    return Response(games_list, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((IsAuthenticated, IsAdminUser))
def all_confirmed_alike_staff(request, game_id):
    response = map(
        lambda x: {
            'id': x.game2.id,
            'title': x.game2.title,
        },
        ConfirmedAlike.objects.filter(game1_id=game_id, confirmed_by='STF'))

    return Response(response, status=status.HTTP_200_OK)


@api_view(['POST', 'DELETE'])
@permission_classes((IsAuthenticated, IsAdminUser))
def alike_admin(request, game1_id, game2_id):
    if request.method == 'POST':
        return alike_admin_post(request, game1_id, game2_id)

    if request.method == 'DELETE':
        return alike_admin_delete(request, game1_id, game2_id)


def alike_admin_post(request, game1_id, game2_id):
    if game1_id == game2_id:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    game1 = get_object_or_404(SwitchGame, id=game1_id)
    game2 = get_object_or_404(SwitchGame, id=game2_id)

    try:
        instance = ConfirmedAlike.objects.get(
            game1=game1, game2=game2, confirmed_by='STF')
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except ConfirmedAlike.DoesNotExist:
        pass

    confirmed_alike1 = ConfirmedAlike(
        game1=game1, game2=game2, confirmed_by='STF')

    confirmed_alike2 = ConfirmedAlike(
        game1=game2, game2=game1, confirmed_by='STF')

    try:
        confirmed_alike1.save()
        confirmed_alike2.save()
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        confirmed_alike1.delete()
        confirmed_alike2.delete()
        return Response(status=status.HTTP_400_BAD_REQUEST)


def alike_admin_delete(request, game1_id, game2_id):
    game1 = get_object_or_404(SwitchGame, id=game1_id)
    game2 = get_object_or_404(SwitchGame, id=game2_id)

    confirmed_alike1 = get_object_or_404(
        ConfirmedAlike, confirmed_by='STF', game1=game1, game2=game2)

    confirmed_alike2 = get_object_or_404(
        ConfirmedAlike, confirmed_by='STF', game1=game1, game2=game2)

    try:
        confirmed_alike1.delete()
        confirmed_alike2.delete()
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        print('Error deleting alike for games {} and {}'
              .format(game1, game2))
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def all_voted_alike_user(request, game_code):
    game = get_object_or_404(SwitchGame, game_code_unique=game_code)

    query = SuggestAlike.objects \
        .filter(game1=game, user=request.user) \
        .annotate(game2_title=Coalesce('game2__game_eu__title',
                                       'game2__game_us__title'))

    response = map(lambda x: {'game_code': x.game2.game_code_unique,
                              'title': x.game2_title}, query)

    return Response(response, status=status.HTTP_200_OK)


@api_view(['POST', 'DELETE'])
@permission_classes((IsAuthenticated,))
def vote_alike(request, game1_code, game2_code):
    if request.method == 'POST':
        return vote_alike_post(request, game1_code, game2_code)

    if request.method == 'DELETE':
        return vote_alike_delete(request, game1_code, game2_code)


def vote_alike_post(request, game1_code, game2_code):
    game1 = get_object_or_404(SwitchGame, game_code_unique=game1_code)
    game2 = get_object_or_404(SwitchGame, game_code_unique=game2_code)

    if game1 == game2:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    # If already exists, raise an error
    try:
        instance = SuggestAlike.objects.get(
            game1=game1, game2=game2, user=request.user)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except SuggestAlike.DoesNotExist:
        pass

    vote_alike1 = SuggestAlike(game1=game1, game2=game2, user=request.user)
    vote_alike2 = SuggestAlike(game1=game2, game2=game1, user=request.user)

    try:
        vote_alike1.save()
        vote_alike2.save()
        confirm_alike_by_vote(game1, game2)
        return Response(status=status.HTTP_200_OK)

    except Exception as e:
        if vote_alike1.id:
            vote_alike1.delete()

        if vote_alike2.id:
            vote_alike2.delete()

        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def vote_alike_delete(request, game1_code, game2_code):
    game1 = get_object_or_404(SwitchGame, game_code_unique=game1_code)
    game2 = get_object_or_404(SwitchGame, game_code_unique=game2_code)

    vote_alike1 = get_object_or_404(
        SuggestAlike, user=request.user, game1=game1, game2=game2)

    vote_alike2 = get_object_or_404(
        SuggestAlike, user=request.user, game1=game2, game2=game1)

    try:
        vote_alike1.delete()
        vote_alike2.delete()
        unconfirm_alike_by_vote(game1, game2)
        return Response(status=status.HTTP_200_OK)

    except Exception as e:
        print('Error deleting alike for games {} and {}'
              .format(game1, game2))
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def confirm_alike_by_vote(game1, game2):
    votes_count = SuggestAlike.objects \
        .filter(game1=game1, game2=game2).count()

    if votes_count >= VOTE_ALIKE_UPPERBOUND:

        if ConfirmedAlike.objects \
                .filter(game1=game1, game2=game2, confirmed_by='VOT') \
                .count() == 0:

            confirmed_alike1 = ConfirmedAlike(
                game1=game1, game2=game2, confirmed_by='VOT')
            confirmed_alike1.save()

        if ConfirmedAlike.objects \
                .filter(game1=game2, game2=game1, confirmed_by='VOT') \
                .count() == 0:

            confirmed_alike2 = ConfirmedAlike(
                game1=game2, game2=game1, confirmed_by='VOT')
            confirmed_alike2.save()


def unconfirm_alike_by_vote(game1, game2):
    votes_count = SuggestAlike.objects \
        .filter(game1=game1, game2=game2).count()

    if votes_count <= VOTE_ALIKE_LOWERBOUND:

        if ConfirmedAlike.objects \
                .filter(game1=game1, game2=game2, confirmed_by='VOT') \
                .count():

            confirmed_alike1 = ConfirmedAlike.objects.get(
                game1=game1, game2=game2, confirmed_by='VOT')
            confirmed_alike1.delete()

        if ConfirmedAlike.objects \
                .filter(game1=game2, game2=game1, confirmed_by='VOT') \
                .count():

            confirmed_alike2 = ConfirmedAlike.objects.get(
                game1=game2, game2=game1, confirmed_by='VOT')
            confirmed_alike2.delete()


@api_view(['GET'])
@permission_classes((IsAuthenticated, IsAdminUser))
def all_unconfirmed_suggested_alike(request):
    confirmed_subquery = ConfirmedAlike.objects \
        .filter(game1=OuterRef('game1'), game2=OuterRef('game2'))

    unconf_sugg_alike = SuggestAlike.objects \
        .annotate(already_confirmed=Exists(confirmed_subquery)) \
        .filter(already_confirmed=False) \
        .annotate(game1_title=Coalesce(
            'game1__game_eu__title', 'game1__game_us__title')) \
        .annotate(game1_image=Coalesce(
            'game1__game_eu__image_sq_h2_url', 'game1__game_us__front_box_art',
            output_field=CharField())) \
        .annotate(game2_title=Coalesce(
            'game2__game_eu__title', 'game2__game_us__title')) \
        .annotate(game2_image=Coalesce(
            'game2__game_eu__image_sq_h2_url', 'game2__game_us__front_box_art',
            output_field=CharField())) \
        .values(
            'game1__id', 'game1__game_code_unique', 'game1_title', 'game1_image',
            'game2__id', 'game2__game_code_unique', 'game2_title', 'game2_image',
        ) \
        .distinct()

    response = list(
        map(lambda alike: {
            'game1': {
                'id': alike['game1__id'],
                'game_code': alike['game1__game_code_unique'],
                'title': alike['game1_title'],
                'game_image': alike['game1_image'],
            },
            'game2': {
                'id': alike['game2__id'],
                'game_code': alike['game2__game_code_unique'],
                'title': alike['game2_title'],
                'game_image': alike['game2_image'],
            },
        }, unconf_sugg_alike)
    )

    return Response(response, status=status.HTTP_200_OK)
