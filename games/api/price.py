from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from games.models import SwitchGamePrice, SwitchGameSale, SwitchGame
from games.serializers import SwitchGameMediaSerializer


@api_view(['GET'])
def all_price_game_code(request, game_code):
    game = get_object_or_404(SwitchGame, game_code_unique=game_code)

    response = {}
    for price in SwitchGamePrice.objects.filter(game=game).order_by('country'):
        response[price.country] = {'price':price.raw_value}

    for sale in SwitchGameSale.objects.filter(game=game).order_by('country'):
        if sale.country not in response:
            response[sale.country] = {}
        response[sale.country]['sale_price'] = sale.raw_value

        if sale.start_datetime:
            response[sale.country]['sale_from'] = sale.start_datetime

        if sale.start_datetime:
            response[sale.country]['sale_to'] = sale.end_datetime

    return Response(response, status=status.HTTP_200_OK)
