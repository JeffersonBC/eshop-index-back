from django.conf.urls import url

from games.api.media import (
    all_media_by_game_code,
    all_media_by_game_id,
    media,
    media_post,
    media_order_up,
    media_order_down,
)


urlpatterns = [
    url(r'^all/by_id/(?P<game_id>\d+)/$',
        all_media_by_game_id),

    url(r'^all/by_code/(?P<game_code>[A-Z0-9]{5})/$',
        all_media_by_game_code),

    url(r'^new/(?P<game_id>\d+)/$',
        media_post),

    # GET, PATCH and DELETE
    url(r'^(?P<id>\d+)/$',
        media),

    url(r'^(?P<id>\d+)/order/up/$',
        media_order_up),

    url(r'^(?P<id>\d+)/order/down/$',
        media_order_down),
]
