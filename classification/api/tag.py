from django.db import IntegrityError
from django.db.models import CharField, Count, Q, F, OuterRef, Exists
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from classification.models import ConfirmedTag, TagGroup, Tag, SuggestedTag
from games.models import SwitchGame
from eshop_crawler.settings import VOTE_TAG_UPPERBOUND, VOTE_TAG_LOWERBOUND

from ..serializers import TagGroupSerializer, TagSerializer


# TAG GROUPS
# **********
@api_view(['GET'])
@permission_classes((IsAuthenticated, IsAdminUser))
def all_tag_groups(request):
    response = map(
        lambda x: {'id': x.id, 'name': x.name},
        TagGroup.objects.all().order_by('name'))

    return Response(response, status=status.HTTP_200_OK)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes((IsAuthenticated, IsAdminUser))
def tag_group(request, id):
    if request.method == 'GET':
        return tag_group_get(request, id)

    elif request.method == 'PATCH':
        return tag_group_update(request, id)

    elif request.method == 'DELETE':
        return tag_group_delete(request, id)


def tag_group_get(request, id):
    instance = get_object_or_404(TagGroup, id=id)
    serialized = TagGroupSerializer(instance=instance)

    return Response(serialized.data, status=status.HTTP_200_OK)


def tag_group_update(request, id):
    tag_group = get_object_or_404(TagGroup, id=id)

    updated_tag_group = TagGroupSerializer(
        data=request.data, instance=tag_group)

    success = updated_tag_group.is_valid()

    if success:
        updated_tag_group.save()
        return Response(status=status.HTTP_200_OK)

    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


def tag_group_delete(request, id):
    tag_group = get_object_or_404(TagGroup, id=id)
    tag_group.delete()

    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsAdminUser))
def tag_group_post(request):

    tag_group = TagGroupSerializer(data=request.data)
    success = tag_group.is_valid()

    if success:
        tag_group.save()
        return Response(status=status.HTTP_200_OK)

    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


# TAGS
# ****
@api_view(['GET'])
def all_tags_of_game(request, game_code):
    game = get_object_or_404(SwitchGame, game_code_unique=game_code)

    tag_groups = {}
    for group in TagGroup.objects.all():
        tag_groups[group.id] = group.name

    tags = {}

    tag_ids = map(
        lambda x: x['tag__id'],
        game.confirmedtag_set.distinct('tag').values('tag__id'))

    conf_tag_query = Tag.objects \
        .filter(id__in=tag_ids) \
        .annotate(votes=Count('suggestedtag',
                              filter=Q(suggestedtag__game=game))) \
        .order_by('-votes', 'name')

    print(conf_tag_query.values('name', 'votes'))

    for tag in conf_tag_query:
        if tag_groups[tag.tag_group.id] not in tags:
            tags[tag_groups[tag.tag_group.id]] = []

        tags[tag_groups[tag.tag_group.id]].append({
            'id': tag.id,
            'name': tag.name,
        })

    return Response(tags, status=status.HTTP_200_OK)


@api_view(['GET'])
def all_tags_by_group(request):
    tag_groups = {}
    for group in TagGroup.objects.all():
        tag_groups[group.id] = group.name

    tags = {}
    for tag in Tag.objects.all().order_by('name'):
        if tag_groups[tag.tag_group.id] not in tags:
            tags[tag_groups[tag.tag_group.id]] = []

        tags[tag_groups[tag.tag_group.id]].append(
            {'id': tag.id, 'name': tag.name}
        )

    return Response(tags, status=status.HTTP_200_OK)


@api_view(['GET'])
def all_tags_by_votable_group(request):
    tag_groups = {}
    for group in TagGroup.objects.filter(allow_vote=True):
        tag_groups[group.id] = group.name

    tags = {}
    for tag in Tag.objects.filter(tag_group__allow_vote=True).order_by('name'):
        if tag_groups[tag.tag_group.id] not in tags:
            tags[tag_groups[tag.tag_group.id]] = []

        tags[tag_groups[tag.tag_group.id]].append(
            {'id': tag.id, 'name': tag.name}
        )

    return Response(tags, status=status.HTTP_200_OK)


@api_view(['GET'])
def all_tags_by_searcheable_group(request):
    tag_groups = {}
    for group in TagGroup.objects.all():
        tag_groups[group.id] = group.name

    tags = {}

    for tag in Tag.objects \
            .annotate(games=Count('confirmedtag__game',
                      filter=Q(confirmedtag__game__hide=False),
                      distinct=True)) \
            .filter(games__gte=F('tag_group__min_games_for_search')) \
            .order_by('name'):

        if tag_groups[tag.tag_group.id] not in tags:
            tags[tag_groups[tag.tag_group.id]] = []

        tags[tag_groups[tag.tag_group.id]].append(
            {'id': tag.id, 'name': tag.name}
        )

    return Response(tags, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((IsAuthenticated, IsAdminUser))
def all_tags(request):
    response = map(
        lambda x: {'id': x.id, 'name': x.name, 'group': x.tag_group.name},
        Tag.objects.all().order_by('tag_group__name','name'))

    return Response(response, status=status.HTTP_200_OK)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes((IsAuthenticated, IsAdminUser))
def tag(request, id):
    if request.method == 'GET':
        return tag_get(request, id)

    elif request.method == 'PATCH':
        return tag_update(request, id)

    elif request.method == 'DELETE':
        return tag_delete(request, id)


def tag_get(request, id):
    tag = get_object_or_404(Tag, id=id)
    response = {
        'id': tag.id,
        'name': tag.name,
        'group': {'id': tag.tag_group.id, 'name': tag.tag_group.name}
    }

    return Response(response, status=status.HTTP_200_OK)


def tag_update(request, id):
    tag = get_object_or_404(Tag, id=id)
    tag_group = get_object_or_404(TagGroup, id=request.data['group_id'])

    updated_tag = TagSerializer(
        data=request.data,
        instance=tag,
        context={'tag_group': tag_group})

    success = updated_tag.is_valid()

    if success:
        updated_tag.save()
        return Response(status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


def tag_delete(request, id):
    tag = get_object_or_404(Tag, id=id)
    tag.delete()

    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsAdminUser))
def tag_post(request):
    tag_group = get_object_or_404(TagGroup, id=request.data['group_id'])

    tag = TagSerializer(
        data=request.data,
        context={'tag_group': tag_group})

    success = tag.is_valid()

    if success:
        tag.save()
        return Response(status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsAdminUser))
def tag_merge(request, tag1_id, tag2_id):
    tag1 = get_object_or_404(Tag, id=tag1_id)
    tag2 = get_object_or_404(Tag, id=tag2_id)

    confirmed_tag2 = ConfirmedTag.objects.filter(tag_id=tag2_id)
    suggested_tag2 = SuggestedTag.objects.filter(tag_id=tag2_id)

    for query in [confirmed_tag2, suggested_tag2]:
        for item in query:
            try:
                item.tag_id = tag1_id
                item.save()
            except IntegrityError:
                item.delete()

    tag2.delete()

    return Response(status=status.HTTP_200_OK)


# CONFIRMED TAGS
# ****
@api_view(['GET'])
@permission_classes((IsAuthenticated, IsAdminUser))
def confirmed_tags_of_game(request, game_id):
    game = get_object_or_404(SwitchGame, id=game_id)

    confirmed_by_nintendo = game.confirmedtag_set.filter(confirmed_by='NTD')
    confirmed_by_staff = game.confirmedtag_set.filter(confirmed_by='STF')

    response = {
        'nintendo': dict(zip(
            map(lambda x: x.tag.id, confirmed_by_nintendo),
            [True] * confirmed_by_nintendo.count(),
        )),

        'staff': dict(zip(
            map(lambda x: x.tag.id, confirmed_by_staff),
            [True] * confirmed_by_staff.count(),
        ))
    }

    return Response(response, status=status.HTTP_200_OK)


@api_view(['POST', 'DELETE'])
@permission_classes((IsAuthenticated, IsAdminUser))
def confirm_tag_staff(request, tag_id, game_id):
    if request.method == 'POST':
        return confirmed_tag_staff_add(request, tag_id, game_id)

    elif request.method == 'DELETE':
        return confirmed_tag_staff_remove(request, tag_id, game_id)


def confirmed_tag_staff_add(request, tag_id, game_id):
    game = get_object_or_404(SwitchGame, id=game_id)
    tag = get_object_or_404(Tag, id=tag_id)

    confirmation = ConfirmedTag(tag=tag, game=game, confirmed_by='STF')
    confirmation.save()

    return Response(status=status.HTTP_200_OK)


def confirmed_tag_staff_remove(request, tag_id, game_id):
    game = get_object_or_404(SwitchGame, id=game_id)
    tag = get_object_or_404(Tag, id=tag_id)

    confirmation = get_object_or_404(
        ConfirmedTag,
        tag=tag, game=game, confirmed_by='STF')

    confirmation.delete()

    return Response(status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes((IsAuthenticated, IsAdminUser))
def unconfirm_tag_nintendo(request, tag_id, game_id):
    instance = get_object_or_404(
        ConfirmedTag, tag_id=tag_id, game_id=game_id, confirmed_by='NTD')

    try:
        instance.delete()
        return Response(status=status.HTTP_200_OK)

    except Exception as e:
        print('Error unconfirming tag {} for game {}'
              .format(tag_id, game_id))
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# VOTE FOR TAG
# ****
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def voted_tags_of_game(request, game_code):
    game = get_object_or_404(SwitchGame, game_code_unique=game_code)
    votes = game.suggestedtag_set.filter(user=request.user)

    response = dict(zip(
        map(lambda x: x.tag.id, votes),
        [True] * votes.count()))

    return Response(response, status=status.HTTP_200_OK)


@api_view(['POST', 'DELETE'])
@permission_classes((IsAuthenticated,))
def vote_tag(request, tag_id, game_code):
    if request.method == 'POST':
        return vote_tag_post(request, tag_id, game_code)

    if request.method == 'DELETE':
        return vote_tag_delete(request, tag_id, game_code)


def vote_tag_post(request, tag_id, game_code):
    game = get_object_or_404(SwitchGame, game_code_unique=game_code)
    tag = get_object_or_404(Tag, id=tag_id)

    # If tag from unvotable group, raise an error
    if not tag.tag_group.allow_vote:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    # If already exists, raise an error
    try:
        instance = SuggestedTag.objects.get(
            game=game, tag=tag, user=request.user)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except SuggestedTag.DoesNotExist:
        pass

    vote_tag = SuggestedTag(game=game, tag=tag, user=request.user)

    try:
        vote_tag.save()
        confirm_tag_by_vote(game, tag)
        return Response(status=status.HTTP_200_OK)

    except Exception as e:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def vote_tag_delete(request, tag_id, game_code):
    game = get_object_or_404(SwitchGame, game_code_unique=game_code)
    tag = get_object_or_404(Tag, id=tag_id)

    vote_tag = get_object_or_404(
        SuggestedTag, game=game, tag=tag, user=request.user)

    try:
        vote_tag.delete()
        unconfirm_tag_by_vote(game, tag)
        return Response(status=status.HTTP_200_OK)

    except Exception as e:
        print('Error deleting alike for games {} and {}'
              .format(game1, game2))
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def confirm_tag_by_vote(game, tag):
    votes_count = SuggestedTag.objects.filter(game=game, tag=tag).count()

    if votes_count >= VOTE_TAG_UPPERBOUND:
        if ConfirmedTag.objects \
                .filter(game=game, tag=tag, confirmed_by='VOT') \
                .count() == 0:

            confirmed = ConfirmedTag(game=game, tag=tag, confirmed_by='VOT')
            confirmed.save()


def unconfirm_tag_by_vote(game, tag):
    votes_count = SuggestedTag.objects.filter(game=game, tag=tag).count()

    if votes_count <= VOTE_TAG_LOWERBOUND:
        if ConfirmedTag.objects \
                .filter(game=game, tag=tag, confirmed_by='VOT') \
                .count():

            confirmed = ConfirmedTag.objects.get(
                game=game, tag=tag, confirmed_by='VOT')
            confirmed.delete()


# SUGGESTED TAGS
# ****
@api_view(['GET'])
@permission_classes((IsAuthenticated, IsAdminUser))
def all_unconfirmed_suggested_tags(request):
    confirmed_subquery = ConfirmedTag.objects \
        .filter(game=OuterRef('game'), tag=OuterRef('tag'))

    unconf_sugg_tags = SuggestedTag.objects \
        .annotate(already_confirmed=Exists(confirmed_subquery)) \
        .filter(already_confirmed=False) \
        .annotate(game_title=Coalesce(
            'game__game_eu__title', 'game__game_us__title')) \
        .annotate(game_image=Coalesce(
            'game__game_eu__image_sq_h2_url', 'game__game_us__front_box_art',
            output_field=CharField())) \
        .values(
            'game__id', 'game__game_code_unique', 'game_title', 'game_image',
            'tag__id', 'tag__name') \
        .distinct()

    response = {}

    for suggestion in unconf_sugg_tags:
        if suggestion['game__id'] not in response:
            response[suggestion['game__id']] = {
                'title': suggestion['game_title'],
                'game_code': suggestion['game__game_code_unique'],
                'game_image': suggestion['game_image'],
                'tags': {},
            }

        response[suggestion['game__id']]['tags'][suggestion['tag__id']] = suggestion['tag__name']

    return Response(response, status=status.HTTP_200_OK)
