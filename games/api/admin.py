from django.db import IntegrityError
from django.db.models import Count, Q, IntegerField, CharField
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from games.models import (
    SwitchGame,
    SwitchGameUS,
    SwitchGameEU,
    SwitchGameMedia,
    SwitchGamePrice,
)

from classification.models import (
    ConfirmedHighlight,
    ConfirmedTag,
    Recomendation,
    Review,
    SuggestedTag,
)


@api_view(['GET'])
@permission_classes((IsAuthenticated, IsAdminUser))
def all_games(request):
    games = SwitchGame.objects.all() \
        .annotate(game_title=Coalesce('game_eu__title', 'game_us__title')) \
        .annotate(game_image=Coalesce(
            'game_eu__image_sq_url', 'game_us__front_box_art',
            output_field=CharField())) \
        .annotate(likes=Count(
            'recomendation',
            filter=Q(recomendation__recomends=True),
            output_field=IntegerField())) \
        .annotate(dislikes=Count(
            'recomendation',
            filter=Q(recomendation__recomends=False),
            output_field=IntegerField())) \
        .annotate(highlighted=Count(
            'confirmedhighlight',
            filter=Q(confirmedhighlight__confirmed_by='STF'),
            output_field=IntegerField())) \
        .order_by('game_title')

    response = []
    for game in games:
        response.append({
            'id': game.id,
            'title': game.game_title,
            'code_unique': game.game_code_unique,
            'likes': game.likes,
            'dislikes': game.dislikes,
            'image_eu_square': game.game_image,
            'highlighted': game.highlighted > 0,
            'hide': game.hide
        })

    return Response(response, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((IsAuthenticated, IsAdminUser))
def game_get_simple(request, game_id):
    game = SwitchGame.objects \
        .filter(id=game_id) \
        .annotate(game_title=Coalesce('game_eu__title', 'game_us__title')) \
        .annotate(game_image=Coalesce(
            'game_eu__image_sq_url', 'game_us__front_box_art',
            output_field=CharField()))

    if game.count() == 0:
        return Response(status=status.HTTP_404_NOT_FOUND)

    response = game_to_json_simple(game[0], request.user)
    return Response(response, status=status.HTTP_200_OK)


@api_view(['POST', 'DELETE'])
@permission_classes((IsAuthenticated, IsAdminUser))
def game_hide(request, game_id):
    game = get_object_or_404(SwitchGame, id=game_id)

    if request.method == 'POST':
        game.hide = True
    elif request.method == 'DELETE':
        game.hide = False

    try:
        game.save()
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsAdminUser))
def game_merge(request, game1_id, game2_id):
    game1 = get_object_or_404(SwitchGame, id=game1_id)
    game2 = get_object_or_404(SwitchGame, id=game2_id)

    # If one of the games is already complete, return error
    if (game1.game_us and game1.game_eu) or (game2.game_us and game2.game_eu):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    # If each game has one different region, merge them. Else return error
    if not game1.game_us and game2.game_us:
        game1.game_us = game2.game_us
    elif not game1.game_eu and game2.game_eu:
        game1.game_eu = game2.game_eu
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    # Copy recomendations, reviews, tag votes and media from game2 to game1
    media = SwitchGameMedia.objects.filter(game_id=game2_id)
    reviews = Review.objects.filter(game_id=game2_id)
    recomendations = Recomendation.objects.filter(game_id=game2_id)
    suggested_tags = SuggestedTag.objects.filter(game_id=game2_id)
    confirmed_tags = ConfirmedTag.objects.filter(
        game_id=game2_id, confirmed_by='NTD')
    prices = SwitchGamePrice.objects.filter(game_id=game2_id)

    # Reorder but don't save yet
    game1_media_count = SwitchGameMedia.objects.filter(game_id=game1_id) \
        .count()

    for m in media:
        m.order = m.order + game1_media_count

    # Try to move recomendations, reviews, suggested/ confirmed tags and media
    for query in [
        media, reviews, recomendations, suggested_tags, confirmed_tags, prices
    ]:
        for item in query:
            item.game_id = game1_id
            try:
                item.save()
            except IntegrityError:
                item.delete()

    try:
        game2.delete()
        game1.save()
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def game_to_json_simple(game, user):

    game_json = {
        'title': game.game_title,
        'game_code': game.game_code_unique,
        'game_image': game.game_image,
    }

    return game_json
