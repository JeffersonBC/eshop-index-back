from django.conf.urls import url

from games.api.price import (
    all_price_game_code,
)


urlpatterns = [
    url(r'^all/by_code/(?P<game_code>[A-Z0-9]{5})/$',
        all_price_game_code),
]
