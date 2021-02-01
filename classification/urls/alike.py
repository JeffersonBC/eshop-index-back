from django.conf.urls import url

from classification.api.alike import (
    all_confirmed_alike,
    all_voted_alike_user,
    vote_alike,

    all_confirmed_alike_staff,
    alike_admin,

    all_unconfirmed_suggested_alike,
)


urlpatterns = [
    url(r'^voted_all/(?P<game_code>[A-Z0-9]{5})/$',
        all_voted_alike_user),
    url(r'^vote/(?P<game1_code>[A-Z0-9]{5})/(?P<game2_code>[A-Z0-9]{5})/$',
        vote_alike),
    url(r'^confirmed/(?P<game_code>[A-Z0-9]{5})/$',
        all_confirmed_alike),


    # ADMIN
    url(r'^admin/confirmed/staff/(?P<game_id>\d+)/$',
        all_confirmed_alike_staff),
    url(r'^admin/(?P<game1_id>\d+)/(?P<game2_id>\d+)/$',
        alike_admin),
    url(r'^admin/suggested/unconfirmed/all/$',
        all_unconfirmed_suggested_alike),
]
