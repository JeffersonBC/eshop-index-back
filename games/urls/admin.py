from django.conf.urls import url

from games.api.admin import (
    all_games,
    game_get_simple,
    game_hide,
    game_merge,
)


urlpatterns = [
    url(r'^admin/all/$',
        all_games),

    url(r'^simple/id/(?P<game_id>\d+)/$',
        game_get_simple),

    url(r'^admin/hide/(?P<game_id>\d+)/$',
        game_hide),

    url(r'^admin/merge/(?P<game1_id>\d+)/(?P<game2_id>\d+)/$',
        game_merge),
]
