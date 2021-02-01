from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from games.models import SwitchGameMedia, SwitchGame
from games.serializers import SwitchGameMediaSerializer


@api_view(['GET'])
def all_media_by_game_code(request, game_code):
    game = get_object_or_404(SwitchGame, game_code_unique=game_code)

    response = map(
        lambda media: {'media_type': media.media_type, 'url': media.url},
        SwitchGameMedia.objects.filter(game=game).order_by('order'))

    return Response(response, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((IsAuthenticated, IsAdminUser))
def all_media_by_game_id(request, game_id):
    game = get_object_or_404(SwitchGame, id=game_id)

    response = map(
        lambda media: {
            'id': media.id,
            'media_type': media.media_type,
            'url': media.url,
        },
        SwitchGameMedia.objects.filter(game=game).order_by('order'))

    return Response(response, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsAdminUser))
def media_post(request, game_id):
    game = get_object_or_404(SwitchGame, id=game_id)
    order = SwitchGameMedia.objects.filter(game=game).count()

    media = SwitchGameMediaSerializer(
        data=request.data,
        context={'game': game, 'order': order},
    )

    if media.is_valid():
        try:
            media.save()
            return Response(status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            print('Server error while adding media for game {}'.format(game))
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET','PATCH','DELETE'])
@permission_classes((IsAuthenticated, IsAdminUser))
def media(request, id):
    if request.method == 'GET':
        return media_get(request, id)

    if request.method == 'PATCH':
        return media_patch(request, id)

    if request.method == 'DELETE':
        return media_delete(request, id)


def media_get(request, id):
    media = get_object_or_404(SwitchGameMedia, id=id)
    response = {'media_type': media.media_type, 'url': media.url}

    return Response(response, status=status.HTTP_200_OK)


def media_patch(request, id):
    instance = get_object_or_404(SwitchGameMedia, id=id)
    serialized = SwitchGameMediaSerializer(data=request.data,
                                           instance=instance)

    if serialized.is_valid():
        try:
            serialized.save()
            return Response(status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            print('Server error while updating media {}'.format(instance.id))
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


def media_delete(request, id):
    instance = get_object_or_404(SwitchGameMedia, id=id)
    media_after = SwitchGameMedia.objects.filter(order__gt=instance.order)

    try:
        instance.delete()

        for m in media_after:
            m.order = m.order - 1
            m.save()

        return Response(status=status.HTTP_200_OK)

    except Exception as e:
        print(e)
        print('Server error while deleting media {}'
            .format(media.id))
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsAdminUser))
def media_order_up(request, id):
    media = get_object_or_404(SwitchGameMedia, id=id)
    media_after = SwitchGameMedia.objects.filter(order=media.order + 1)

    if media_after.count():
        m_after = media_after[0]

        media.order = media.order + 1
        m_after.order = m_after.order - 1

        try:
            media.save()
            m_after.save()
            return Response(status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    else:
        return Response(status=status.HTTP_304_NOT_MODIFIED)


@api_view(['POST'])
@permission_classes((IsAuthenticated, IsAdminUser))
def media_order_down(request, id):
    media = get_object_or_404(SwitchGameMedia, id=id)
    media_before = SwitchGameMedia.objects.filter(order=media.order - 1)

    if media_before.count():
        m_before = media_before[0]

        media.order = media.order - 1
        m_before.order = m_before.order + 1

        try:
            media.save()
            m_before.save()
            return Response(status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    else:
        return Response(status=status.HTTP_304_NOT_MODIFIED)
