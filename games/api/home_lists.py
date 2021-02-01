import json
from random import randint

from django.contrib.auth.models import AnonymousUser
from django.db.models import Count, OuterRef, Exists
from django.db.models.functions import Least
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from games.api.game import games_all_base_query, game_to_json
from games.api.queries import search_query
from games.models import SwitchGameList, SwitchGameListSlot
from games.serializers import SwitchGameListSerializer


# SLOTS
@api_view(['GET'])
@permission_classes((IsAuthenticated, IsAdminUser))
def all_list_slots(request):
    slot_dict = {}
    for slot in SwitchGameListSlot.objects.all().order_by('order'):
        slot_dict[slot.id] = {
            'id': slot.id,
            'order': slot.order,
            'lists': []
        }

    for game_list in SwitchGameList.objects.all().order_by('title'):
        slot_dict[game_list.slot.id]['lists'].append({
            'id': game_list.id,
            'title': game_list.title,
            'query_json': game_list.query_json,
            'frequency': game_list.frequency,
        })

    msg = map(lambda slot_id: slot_dict[slot_id], slot_dict)

    return Response(msg, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsAdminUser))
def list_slot_post(request):
    slot_count = SwitchGameListSlot.objects.count()
    new_slot = SwitchGameListSlot(order=slot_count)

    try:
        new_slot.save()
    except Exception as e:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes((IsAuthenticated, IsAdminUser))
def list_slot_delete(request, id):
    instance = get_object_or_404(SwitchGameListSlot, id=id)
    slots_after = SwitchGameListSlot.objects.filter(order__gt=instance.order)

    try:
        instance.delete()
        for slot_after in slots_after:
            slot_after.order = slot_after.order - 1
            slot_after.save()
    except Exception as e:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsAdminUser))
def list_slot_order_up(request, id):
    slot = get_object_or_404(SwitchGameListSlot, id=id)
    slots_after = SwitchGameListSlot.objects.filter(order=slot.order + 1)

    if slots_after.count():
        slot_after = slots_after[0]

        slot.order = slot.order + 1
        slot_after.order = slot_after.order - 1

        try:
            slot.save()
            slot_after.save()
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(status=status.HTTP_304_NOT_MODIFIED)


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsAdminUser))
def list_slot_order_down(request, id):
    slot = get_object_or_404(SwitchGameListSlot, id=id)
    slots_before = SwitchGameListSlot.objects.filter(order=slot.order - 1)

    if slots_before.count():
        slot_before = slots_before[0]

        slot.order = slot.order - 1
        slot_before.order = slot_before.order + 1

        try:
            slot.save()
            slot_before.save()
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(status=status.HTTP_304_NOT_MODIFIED)


# LISTS
@api_view(['POST'])
@permission_classes((IsAuthenticated, IsAdminUser))
def list_post(request, slot_id):
    slot = get_object_or_404(SwitchGameListSlot, id=slot_id)

    new_list = SwitchGameListSerializer(
        data=request.data,
        context={'slot': slot})

    success = new_list.is_valid()

    if success:
        try:
            new_list.save()
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes((IsAuthenticated, IsAdminUser))
def game_list(request, list_id):
    if request.method == 'GET':
        return game_list_get(request, list_id)

    elif request.method == 'PATCH':
        return game_list_update(request, list_id)

    elif request.method == 'DELETE':
        return game_list_delete(request, list_id)


def game_list_get(request, list_id):
    list_instance = get_object_or_404(SwitchGameList, id=list_id)
    serialized = SwitchGameListSerializer(instance=list_instance)

    return Response(serialized.data, status=status.HTTP_200_OK)


def game_list_update(request, list_id):
    list_instance = get_object_or_404(SwitchGameList, id=list_id)

    list_serialized = SwitchGameListSerializer(
        instance=list_instance,
        data=request.data)

    success = list_serialized.is_valid()

    if success:
        try:
            list_serialized.save()
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


def game_list_delete(request, list_id):
    list_instance = get_object_or_404(SwitchGameList, id=list_id)

    try:
        list_instance.delete()
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    try:
        list_instance.delete()
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# QUERIES
@api_view(['GET'])
def game_lists_results(request):
    country = request.query_params.get('country', 'US')

    user = request.user
    slot_dict = {}
    list_slots = SwitchGameListSlot.objects.all()

    # If user not logged, ignore logged lists
    if type(user) == AnonymousUser:
        logged_list_subquery = SwitchGameList.objects \
            .filter(slot_id=OuterRef('pk'), logged_list=False)

        list_slots = list_slots \
            .annotate(has_not_logged=Exists(logged_list_subquery)) \
            .filter(has_not_logged=True)

    # Initialize slot_dicts
    for slot in list_slots \
            .annotate(lists=Count('switchgamelist')) \
            .filter(lists__gte=1) \
            .order_by('order'):

        slot_dict[slot.id] = {'lists': [], 'games': [], 'title': ''}

    # If user not logged, ignore logged lists
    lists = SwitchGameList.objects.all()
    if type(user) == AnonymousUser:
        lists = lists.filter(logged_list=False)

    for game_list in lists:
        slot_dict[game_list.slot.id]['lists'].append({
            'title': game_list.title,
            'query_json': game_list.query_json,
            'frequency': game_list.frequency
        })

    slots = list(map(lambda slot_id: slot_dict[slot_id], slot_dict))

    # For each slot, randomly pick a list based on each list's frequency
    for slot in slots:
        max_freq = 0
        for game_list in slot['lists']:
            max_freq = max_freq + game_list['frequency']

        random_int = randint(1, max_freq)

        for game_list in slot['lists']:
            random_int = random_int - game_list['frequency']

            if random_int <= 0:
                slot['title'] = game_list['title']
                slot['json'] = game_list['query_json']
                slot.pop('lists')
                break

    for slot in slots:
        list_json = json.loads(slot['json'])
        slot.pop('json')

        tags = list_json['tags'].split(',') if 'tags' in list_json else None
        order_by = list_json['order_by'] if 'order_by' in list_json else '-game_title'

        released_status = list_json['released_status'] if 'released_status' in list_json else None
        date_from = list_json['date_from'] if 'date_from' in list_json else None
        date_to = list_json['date_to'] if 'date_to' in list_json else None

        price_from = list_json['price_from'] if 'price_from' in list_json else None
        price_to = list_json['price_to'] if 'price_to' in list_json else None
        sales_only = list_json['sales_only'] if 'sales_only' in list_json else None
        min_discount = list_json['min_discount'] if 'min_discount' in list_json else None

        highlights_only = list_json['highlights_only'] if 'highlights_only' in list_json else None
        unrated_only = list_json['unrated_only'] if 'unrated_only' in list_json else None
        quantity = list_json['qtd'] if 'qtd' in list_json else 20

        # Changes price from/ to in countries with "bigger" currencies
        if price_from:
            price_from = currencyMultiplier(price_from, country)
            slot['title'] = slot['title'].replace(
                '{{price_from}}',
                currencyFormat(price_from, country)
            )

        if price_to:
            price_to = currencyMultiplier(price_to, country)
            slot['title'] = slot['title'].replace(
                '{{price_to}}',
                currencyFormat(price_to, country)
            )


        games = search_query(
            user=request.user,
            search_text=None,
            tags=tags,
            order_by=order_by,
            released_status=released_status,
            date_from=date_from,
            date_to=date_to,
            price_from=price_from,
            price_to=price_to,
            sales_only=sales_only,
            min_discount=min_discount,
            highlights_only=highlights_only,
            unrated_only=unrated_only,
            quantity=quantity,
            offset=0,
            country=country,
        )

        for game in games:
            slot['games'].append(game_to_json(game, request.user))

    return Response(slots, status=status.HTTP_200_OK)


def currencyMultiplier(value, country):
    if country == 'MX':
        return float(value) * 25

    elif country == 'RU':
        return float(value) * 75

    elif country == 'ZA':
        return float(value) * 12.5

    return float(value)


def currencyFormat(value, country='US'):
    if country in ['AR', 'CA', 'CL', 'US']:
        value = "${0:.2f}".format(value)

    elif country in ['FR', 'DE']:
        value = '{0:.2f} €'.format(value)

    elif country in ['BR']:
        value = 'R$ {0:.2f}'.format(value)

    elif country in ['GB']:
        value = '£{0:.2f}'.format(value)

    elif country in ['MX']:
        value = '${0:.2f}'.format(value)

    elif country in ['RU']:
        value = '{0:.0f} RUB'.format(value)

    elif country in ['ZA']:
        value = 'R{0:.2f}'.format(value)

    return value
