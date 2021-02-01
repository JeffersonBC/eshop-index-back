from django.contrib.auth.models import AnonymousUser
from users.models import Following


def user_to_profile_json(user, request):
    profile_json = {
        'username': user.username,
    }

    if user.id == request.user.id:
        profile_json['is_following'] = None
    elif type(request.user) == AnonymousUser:
        profile_json['is_following'] = False
    else:
        profile_json['is_following'] = Following.objects.filter(
            follower=request.user, followed=user).exists()

    return profile_json


def user_to_card_json(user):
    json = {}

    json['username'] = user.username
    json['likes'] = user.recomendation_set.filter(recomends=True).count()
    json['dislikes'] = user.recomendation_set.filter(recomends=False).count()
    json['reviews'] = user.review_set.count()

    return json
