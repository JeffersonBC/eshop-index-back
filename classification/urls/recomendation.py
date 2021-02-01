from django.conf.urls import url

from ..api.recomendation import (
    recomendation,
    current_user_recomendations,
    current_user_all_recomendations,
    username_user_recomendations,
    username_user_all_recomendations,

    highlight_admin,
)


urlpatterns = [
    url(r'^(?P<game_code>[A-Z0-9]{5})/$',
        recomendation),

    url(r'^user_self/all/(?P<recomends>likes|dislikes)/$',
        current_user_all_recomendations),

    url(r'^user_self/$',
        current_user_recomendations),

    url(r'^user/(?P<username>.+)/all/(?P<recomends>likes|dislikes)/$',
        username_user_all_recomendations),

    url(r'^user/(?P<username>.+)/$',
        username_user_recomendations),


    # ADMIN
    url(r'^admin/confirm/(?P<game_id>\d+)/$',
        highlight_admin),
]
