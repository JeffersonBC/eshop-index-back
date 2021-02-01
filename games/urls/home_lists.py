from django.conf.urls import url
from games.api.home_lists import (
    all_list_slots,
    list_slot_post,
    list_slot_delete,
    list_slot_order_up,
    list_slot_order_down,

    list_post,
    game_list,
    game_lists_results,
)


urlpatterns = [
    # SLOTS
    url(r'^admin/game_list/slot/all/$',
        all_list_slots),

    url(r'^admin/game_list/slot/new/$',
        list_slot_post),

    url(r'^admin/game_list/slot/(?P<id>\d+)/delete/$',
        list_slot_delete),

    url(r'^admin/game_list/slot/(?P<id>\d+)/order_up/$',
        list_slot_order_up),

    url(r'^admin/game_list/slot/(?P<id>\d+)/order_down/$',
        list_slot_order_down),

    # LISTS
    url(r'^admin/game_list/slot/(?P<slot_id>\d+)/new_list/$',
        list_post),

    url(r'^admin/game_list/(?P<list_id>\d+)/$',
        game_list),

    url(r'^game_lists/$',
        game_lists_results),
]