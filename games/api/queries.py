from datetime import datetime, timedelta
from functools import reduce
from operator import or_
from random import randint
from re import split

from django.contrib.auth.models import AnonymousUser
from django.contrib.postgres.search import (
    SearchQuery, SearchRank, SearchVector)
from django.db.models import Count, Q, F
from django.db.models.functions import Least, Greatest
from django.shortcuts import get_object_or_404
from django.utils.timezone import now

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from games.models import SwitchGame
from games.api.game import (
    games_all_base_query,
    games_all_base_query_no_user,
    games_apply_user_query,
    game_to_json
)

from classification.models import (
    ConfirmedAlike,
    ConfirmedHighlight,
    ConfirmedTag,
    Recomendation,
    Tag,
)


@api_view(['GET'])
def games_get(request):
    quantity = request.query_params.get('qtd', None)
    offset = request.query_params.get('offset', 0)

    search_text = request.query_params.get('text', '')
    tags = request.query_params.get('tags', None)

    order_by = request.query_params.get('order_by', None)
    released_status = request.query_params.get('released', None)
    date_from = request.query_params.get('date_from', None)
    date_to = request.query_params.get('date_to', None)

    price_from = request.query_params.get('price_from', None)
    price_to = request.query_params.get('price_to', None)
    sales_only = request.query_params.get('sales_only', None)
    min_discount = request.query_params.get('min_discount', None)

    highlights_only = request.query_params.get('highlights_only', None)
    unrated_only = request.query_params.get('unrated_only', None)

    country = request.query_params.get('country', 'US')

    if quantity:
        quantity = int(quantity)
    if offset:
        offset = int(offset)
    if min_discount:
        min_discount = int(min_discount)
    if tags:
        tags = tags.split(',')

    msg = []
    games = search_query(
        user=request.user,
        search_text=search_text,
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
        offset=offset,
        country=country,
    )

    for game in games:
        msg.append(game_to_json(game, request.user))

    return Response(msg, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def games_get_alike_to_recomended(request):
    country = request.query_params.get('country', 'US')

    liked = request.user.recomendation_set \
        .filter(recomends=True) \
        .filter(game__alike_game1__isnull=False) \
        .values('game_id') \
        .distinct()

    if liked.count() == 0:
        return Response(status=status.HTTP_404_NOT_FOUND)

    liked = list(liked)

    random_index = randint(0, len(liked) - 1)
    random_game_id = liked[random_index]['game_id']

    chosen_game_title = games_all_base_query() \
        .get(id=random_game_id).game_title

    alike_query = ConfirmedAlike.objects \
        .filter(game1_id=random_game_id) \
        .annotate(votes=Count('game2__suggested_alike_game2',
                              filter=Q(game1_id=random_game_id))) \
        .order_by('-votes') \
        .values('game2_id')

    games_ids = map(lambda x: x['game2_id'], alike_query)

    games_query = games_all_base_query(request.user, country) \
        .filter(id__in=games_ids)

    games_list = []
    for game in games_query:
        # If game already in games_list list, skip it
        if len(games_list) and \
                games_list[-1]['game_code'] == game.game_code_unique:
            continue

        games_list.append(game_to_json(game, request.user))

    response = {'game_title': chosen_game_title, 'games': games_list}

    return Response(response, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def games_get_recomended_following(request):
    quantity = request.query_params.get('qtd', None)
    offset = request.query_params.get('offset', 0)
    country = request.query_params.get('country', 'US')

    if quantity:
        quantity = int(quantity)
    if offset:
        offset = int(offset)

    following = map(lambda x: x['followed_id'],
                    request.user.follower.values('followed_id'))

    today = now()
    date_lowerbound = today + timedelta(days=-6 * 30)

    game_ids = map(
        lambda x: x['game_id'],
        Recomendation.objects
                     .filter(date__gte=date_lowerbound)
                     .filter(user__in=following)
                     .filter(recomends=True)
                     .values('game_id'))

    games = games_all_base_query(request.user, country) \
        .filter(id__in=game_ids) \
        .distinct() \
        .order_by('-vote_sum')[
            offset: offset + quantity if quantity else None
        ]

    response = []
    for game in games:
        response.append(game_to_json(game, request.user))

    return Response(response, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def games_get_liked_tag(request):
    quantity = request.query_params.get('qtd', None)
    offset = request.query_params.get('offset', 0)
    country = request.query_params.get('country', 'US')

    if quantity:
        quantity = int(quantity)
    if offset:
        offset = int(offset)

    # Randomly choose a tag from a liked game
    liked_games_ids = map(
        lambda x: x['game_id'],
        Recomendation.objects
                     .filter(recomends=True, user=request.user)
                     .values('game_id'))

    liked_tags = list(ConfirmedTag.objects.filter(game_id__in=liked_games_ids)
                                          .values('tag_id', 'tag__name')
                                          .order_by('tag_id'))

    if len(liked_tags) == 0:
        return Response(status=status.HTTP_404_NOT_FOUND)

    random_index = randint(0, len(liked_tags) - 1)
    random_tag_id = liked_tags[random_index]['tag_id']

    # Return the best ranked games from the chosen tag
    games_ids = map(
        lambda x: x['game_id'],
        ConfirmedTag.objects.filter(tag_id=random_tag_id).values('game_id'))

    today = now()
    date_lowerbound = today + timedelta(days=-8 * 30)

    games_query = games_all_base_query(request.user, country) \
        .filter(id__in=games_ids) \
        .annotate(release_date=Greatest('release_us', 'release_eu')) \
        .filter(release_date__gte=date_lowerbound) \
        .order_by('-vote_sum')[offset: offset + quantity if quantity else None]

    response = {
        'tag': Tag.objects.get(id=random_tag_id).name,
        'games': []}

    for game in games_query:
        response['games'].append(game_to_json(game, request.user))

    return Response(response, status=status.HTTP_200_OK)


@api_view(['GET'])
def games_get_random_tag(request):
    quantity = request.query_params.get('qtd', None)
    offset = request.query_params.get('offset', 0)
    country = request.query_params.get('country', 'US')

    if quantity:
        quantity = int(quantity)
    if offset:
        offset = int(offset)

    # Randomly choose a tag with a minimum of 4 games
    tags = Tag.objects \
        .annotate(
            games=Count(
                'confirmedtag__game',
                filter=Q(confirmedtag__game__hide=False),
                distinct=True
            )
        ) \
        .filter(games__gte=16) \
        .values('id', 'games')

    all_tags_ids = [x['id'] for x in tags]

    if len(all_tags_ids) == 0:
        return Response(status=status.HTTP_404_NOT_FOUND)

    random_index = randint(0, len(all_tags_ids) - 1)
    random_tag_id = all_tags_ids[random_index]

    # Return the best ranked games from the chosen tag
    games_ids = map(
        lambda x: x['game_id'],
        ConfirmedTag.objects.filter(tag_id=random_tag_id).values('game_id'))

    today = now()
    date_lowerbound = today + timedelta(days=-8 * 30)

    games_query = games_all_base_query(request.user, country) \
        .filter(id__in=games_ids) \
        .annotate(release_date=Greatest('release_us', 'release_eu')) \
        .filter(release_date__gte=date_lowerbound) \
        .order_by('-vote_sum')[
            offset: offset + quantity if quantity else None]

    response = {
        'tag': Tag.objects.get(id=random_tag_id).name,
        'games': []}

    for game in games_query:
        response['games'].append(game_to_json(game, request.user))

    return Response(response, status=status.HTTP_200_OK)


def search_query(
    user,
    search_text=None,
    tags=None,
    order_by=None,
    released_status=None,
    date_from=None,
    date_to=None,
    price_from=None,
    price_to=None,
    sales_only=None,
    min_discount=None,
    highlights_only=None,
    unrated_only=False,
    quantity=None,
    offset=0,
    country='US',
):

    games = games_all_base_query_no_user(country)

    # PRICE
    if sales_only:
        games = games.filter(sales_value__isnull=False)

    if price_from:
        games = games.filter(current_price__gte=price_from)
    if price_to:
        games = games.filter(current_price__lte=price_to)
    if min_discount:
        min_discount = min_discount / 100
        games = games.filter(discount_percent__gte=min_discount)

    # RELEASE STATUS
    if released_status or (order_by == 'date' or order_by == '-date'):
        games = games.annotate(date=Least('release_us', 'release_eu'))

    if released_status == 'released':
        games = games.filter(date__lte=now())
    elif released_status == 'unreleased':
        games = games.filter(date__gt=now())
    elif released_status == 'latest':
        today = now()
        games = games.filter(
            date__lt=today, date__gt=today + timedelta(days=-4 * 30))
    elif released_status == 'between':
        if date_from:
            games = games.filter(date__gte=date_from)
        if date_to:
            games = games.filter(date__lte=date_to)

    # TAGS
    if tags:
        for tag in tags:
            games = games.filter(confirmedtag__tag_id=tag)

    # HIGHLIGHTS ONLY
    if highlights_only:
        games = games.filter(confirmedhighlight__isnull=False)

    # SEARCH TEXT
    if search_text:
        terms = [SearchQuery(term) for term in split(r'\W+', search_text)]
        vector = SearchVector('game_title')
        query = reduce(or_, terms)

        games = games \
            .annotate(rank=SearchRank(vector, query)) \
            .filter(rank__gte=0.02)

    # SEARCH ORDER
    if order_by:
        # If the search_text is empty there's no 'rank' annotated
        if not (order_by == '-rank' and not search_text):
            games = games.order_by(order_by, 'game_title')
        else:
            games = games.order_by('game_title')

        # If ordering by price, exclude games without price
        if order_by == 'current_price' or order_by == '-current_price':
            games = games.filter(current_price__isnull=False)

        if order_by == 'discount_percent' or order_by == '-discount_percent':
            games = games.filter(discount_percent__isnull=False)

    # ANNOTATES USER LIKES, DISLIKES, REVIEWS AND WISHES
    games = games_apply_user_query(games, user)

    # ONLY GAMES ALREADY RATED BY THE USER
    if unrated_only:
        if user and type(user) != AnonymousUser:
            games = games \
                .exclude(has_liked=True) \
                .exclude(has_disliked=True)

    # PAGINATION
    games = games[offset: offset + quantity if quantity else None]

    return games
