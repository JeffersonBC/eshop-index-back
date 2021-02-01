from django.conf.urls import url

from games.api.game import (
    game_get,

    all_games_select_id,
    all_games_select_game_code,
)


urlpatterns = [
    url(r'^code/(?P<game_code>[A-Z0-9]{5})/$',
        game_get),

    url(r'^all_select/id$',
        all_games_select_id),

    url(r'^all_select/game_code$',
        all_games_select_game_code),
]
