from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from classification.models import Wishlist
from games.api.game import games_all_base_query, game_to_json
from games.models import SwitchGame
from django.db.models import F, Q


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def wishlist(request):
    country = request.query_params.get('country', 'US')

    games = games_all_base_query(request.user, country) \
        .filter(wishlist__user=request.user) \
        .annotate(wish_date=F('wishlist__date')) \
        .filter(has_wish__gte=1) \
        .order_by('-wish_date')

    # 'has_wish' filter is necessary because 'wish_date' annotate brings
    # duplicates

    response = []
    for game in games:
        response.append(game_to_json(game, request.user))

    return Response(response, status=status.HTTP_200_OK)


@api_view(['POST', 'DELETE'])
@permission_classes((IsAuthenticated,))
def wishlist_item(request, game_code):
    if request.method == 'POST':
        return wishlist_item_post(request, game_code)

    elif request.method == 'DELETE':
        return wishlist_item_delete(request, game_code)


def wishlist_item_post(request, game_code):
    game = get_object_or_404(SwitchGame, game_code_unique=game_code)

    if Wishlist.objects.filter(game=game, user=request.user).count() > 0:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    new_wishlist_item = Wishlist(game=game, user=request.user)

    try:
        new_wishlist_item.save()
        return Response(status=status.HTTP_200_OK)

    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST)


def wishlist_item_delete(request, game_code):
    game = get_object_or_404(SwitchGame, game_code_unique=game_code)
    instance = get_object_or_404(Wishlist, game=game, user=request.user)

    try:
        instance.delete()
        return Response(status=status.HTTP_200_OK)

    except Exception as e:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
