from django.contrib.auth import get_user_model
from django.db.models import F
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from classification.models import Recomendation
from classification.serializers import recomendation_to_json
from classification.api.recomendation import recomendation_all_base_query
from users.models import Following
from users.serializers.user_profile import user_to_card_json


@api_view(['POST', 'DELETE'])
@permission_classes((IsAuthenticated,))
def follow_by_username(request, username):
    if request.method == 'POST':
        followed = get_object_or_404(get_user_model(), username=username)

        follow = Following(follower=request.user, followed=followed)
        follow.save()

        return Response(status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        followed = get_object_or_404(get_user_model(), username=username)

        follow = get_object_or_404(
            Following,
            follower=request.user,
            followed=followed)
        follow.delete()

        return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def newsfeed(request):
    users_following = list(map(
        lambda x: x.followed,
        request.user.follower.all()
    ))

    news = recomendation_all_base_query() \
        .annotate(username=F('user__username')) \
        .filter(user__in=users_following) \
        .order_by('-date')[:30]

    response = list(map(lambda x: {
        'game': recomendation_to_json(x, request.user),
        'username': x.username,
        'recomends': x.recomends,
    }, news))

    return Response(response, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def user_following(request):
    following = request.user.follower.all()
    response = list(map(lambda x: user_to_card_json(x.followed), following))

    return Response(
        response,
        status=status.HTTP_200_OK)
