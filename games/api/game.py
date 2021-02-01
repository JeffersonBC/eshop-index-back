from datetime import datetime
from random import randint

from django.contrib.auth.models import AnonymousUser
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import (
    CharField, IntegerField, FloatField,
    F, Q,
    Count,
    Subquery, OuterRef, Exists,
    When, Case, Value,
)
from django.db.models.functions import Coalesce

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from games.models import (
    SwitchGame,
    SwitchGameUS,
    SwitchGameEU,
    SwitchGamePrice,
    SwitchGameSale,
)

from classification.models import (
    ConfirmedAlike,
    ConfirmedHighlight,
    ConfirmedTag,
    Recomendation,
    Review,
    Tag,
    Wishlist,
)


@api_view(['GET'])
def all_games_select_id(request):
    games = SwitchGame.objects \
        .filter(hide=False) \
        .annotate(game_title=Coalesce('game_eu__title', 'game_us__title')) \
        .order_by('game_title')

    response = map(lambda game: {
        'id': game.id,
        'title': game.game_title
    },
        games)

    return Response(response, status=status.HTTP_200_OK)


@api_view(['GET'])
def all_games_select_game_code(request):
    games = games_all_base_query() \
        .filter(hide=False) \
        .order_by('game_title')

    response = map(lambda game: {
        'game_code': game.game_code_unique,
        'title': game.game_title
    },
        games)

    return Response(response, status=status.HTTP_200_OK)


@api_view(['GET'])
def game_get(request, game_code):
    game = games_all_base_query(request.user) \
        .filter(game_code_unique=game_code) \
        .annotate(game_description=F('game_eu__description')) \
        .annotate(link_us=F('game_us__slug')) \
        .annotate(link_eu=F('game_eu__url'))

    if game.count() == 0:
        return Response(status=status.HTTP_404_NOT_FOUND)

    else:
        response = game_to_json(game[0], request.user)
        return Response(response, status=status.HTTP_200_OK)


# UTIL
def game_to_json(game, user):
    if type(user) == AnonymousUser:
        user = None

    recomends = None
    if hasattr(game, 'has_liked') and game.has_liked:
        recomends = True
    elif hasattr(game, 'has_disliked') and game.has_disliked:
        recomends = False

    game_json = {
        'title': game.game_title,
        'game_code': game.game_code_unique,
        'game_image': game.game_image,
        'release_us': game.release_us,
        'release_eu': game.release_eu,
        'likes': game.likes,
        'dislikes': game.dislikes,
        'reviews': game.reviews,
        'tags': game.tags,
        'recomends': recomends,
        'has_review': game.has_review if hasattr(game, 'has_review') else False,
        'has_wish': game.has_wish if hasattr(game, 'has_wish') else False,
    }

    if hasattr(game, 'game_description'):
        game_json['game_description'] = game.game_description

    if hasattr(game, 'link_us'):
        game_json['link_us'] = game.link_us

    if hasattr(game, 'link_eu'):
        game_json['link_eu'] = game.link_eu

    if game.price_value != None:
        game_json['price'] = game.price_value

    if game.sales_value != None:
        game_json['sale_price'] = game.sales_value

    if game.discount_percent != None:
        game_json['discount_percent'] = game.discount_percent

    return game_json


def games_all_base_query(user=None, country='US'):
    query = games_all_base_query_no_user(country)

    if user and type(user) != AnonymousUser:
        query = games_apply_user_query(query, user)

    return query


def games_all_base_query_no_user(country):
    price_subquery = SwitchGamePrice.objects \
        .filter(game=OuterRef('pk'), country=country)

    sales_subquery = SwitchGameSale.objects \
        .filter(game=OuterRef('pk'), country=country)

    query = SwitchGame.objects \
        .filter(hide=False) \
        .annotate(game_title=Coalesce('game_eu__title', 'game_us__title')) \
        .annotate(game_image=Coalesce(
            'game_eu__image_sq_h2_url', 'game_us__front_box_art',
            output_field=CharField())) \
        .annotate(release_us=F('game_us__release_date')) \
        .annotate(release_eu=F('game_eu__release_date')) \
        .annotate(likes=Count(
            'recomendation',
            distinct=True,
            filter=Q(recomendation__recomends=True),
            output_field=IntegerField())) \
        .annotate(dislikes=Count(
            'recomendation',
            distinct=True,
            filter=Q(recomendation__recomends=False),
            output_field=IntegerField())) \
        .annotate(reviews=Count(
            'review',
            distinct=True,
            output_field=IntegerField())) \
        .annotate(tags=ArrayAgg('confirmedtag__tag__name', distinct=True)) \
        .annotate(vote_sum=F('likes') - F('dislikes')) \
        .annotate(price_value=Subquery(price_subquery.values('raw_value'))) \
        .annotate(sales_value=Subquery(sales_subquery.values('raw_value'))) \
        .annotate(current_price=Coalesce('sales_value', 'price_value')) \
        .annotate(discount_percent=
            Case(
                When(price_value__exact=0, then=(Value(0))),
                default=(F('price_value') - F('current_price')) / F('price_value'),
                output_field=FloatField(),
            )
        )

    return query


def games_apply_user_query(query, user=None):
    if user and type(user) != AnonymousUser:
        like_subquery = Recomendation.objects \
            .filter(game=OuterRef('pk'), user=user, recomends=True)

        dislike_subquery = Recomendation.objects \
            .filter(game=OuterRef('pk'), user=user, recomends=False)

        review_subquery = Review.objects \
            .filter(game=OuterRef('pk'), user=user)

        wish_subquery = Wishlist.objects \
            .filter(game=OuterRef('pk'), user=user)

        query = query \
            .annotate(has_liked=Exists(like_subquery)) \
            .annotate(has_disliked=Exists(dislike_subquery)) \
            .annotate(has_review=Exists(review_subquery)) \
            .annotate(has_wish=Exists(wish_subquery))

    return query
