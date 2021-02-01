from django.conf.urls import url

from games.api.queries import (
    games_get,
    games_get_alike_to_recomended,
    games_get_liked_tag,
    games_get_random_tag,
    games_get_recomended_following,
)


urlpatterns = [
    url(r'^$',
        games_get),

    url(r'^alike_recomended/$',
        games_get_alike_to_recomended),

    url(r'^liked_tag/$',
        games_get_liked_tag),

    url(r'^random_tag/$',
        games_get_random_tag),

    url(r'^recomended_following/$',
        games_get_recomended_following),
]
