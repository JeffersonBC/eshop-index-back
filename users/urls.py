from django.conf.urls import url

from rest_framework_jwt.views import (
    obtain_jwt_token,
    refresh_jwt_token,
    # verify_jwt_token
)

from users.api.user import (
    current_user,
    user_profile_by_username,

    user_create,
    user_activate,
    user_password_reset,
    user_send_password_reset_email,
    user_resend_activation_email,

    verify_admin,
    verify_token,
)

from users.api.follow import (
    follow_by_username,
    newsfeed,
    user_following,
)


urlpatterns = [
    # AUTHENTICATION
    url(r'^token_get/$',
        obtain_jwt_token),
    url(r'^token_refresh/$',
        refresh_jwt_token),
    url(r'^token_verify/$',
        verify_token),
    url(r'^admin_verify/$',
        verify_admin),

    # USER DATA
    url(r'^get/$',
        current_user),
    url(r'^create/$',
        user_create),
    url(r'^activate/$',
        user_resend_activation_email),
    url(r'^activate/(?P<user_id_b64>.+)/(?P<token>.+)/$',
        user_activate),
    url(r'^password/reset/$',
        user_send_password_reset_email),
    url(r'^password/reset/(?P<user_id_b64>.+)/(?P<token>.+)/$',
        user_password_reset),
    url(r'^get_by_username/(?P<username>.+)/$',
        user_profile_by_username),



    # FOLLOWING
    url(r'^follow/by_username/(?P<username>.+)/$',
        follow_by_username),
    url(r'^newsfeed/$',
        newsfeed),
    url(r'^following/$',
        user_following),
]
