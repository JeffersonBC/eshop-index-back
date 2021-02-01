from django.conf.urls import url

from ..api.tag import (
    all_tag_groups,
    tag_group,
    tag_group_post,

    all_tags_of_game,
    all_tags_by_group,
    all_tags_by_searcheable_group,
    all_tags_by_votable_group,
    all_tags,
    tag,
    tag_post,
    tag_merge,

    confirmed_tags_of_game,
    confirm_tag_staff,
    unconfirm_tag_nintendo,

    voted_tags_of_game,
    vote_tag,

    all_unconfirmed_suggested_tags,
)


urlpatterns = [
    # TAG GROUPS
    url(r'^groups/$',
        all_tag_groups),
    url(r'^group/(?P<id>\d+)/$',
        tag_group),
    url(r'^group/new/$',
        tag_group_post),


    # TAG
    url(r'^by_game/(?P<game_code>[A-Z0-9]{5})/$',
        all_tags_of_game),
    url(r'^all/$',
        all_tags),
    url(r'^all/by_group/$',
        all_tags_by_group),
    url(r'^all/by_searcheable_group/$',
        all_tags_by_searcheable_group),
    url(r'^all/by_votable_group/$',
        all_tags_by_votable_group),
    url(r'^(?P<id>\d+)/$',
        tag),
    url(r'^new/$',
        tag_post),
    url(r'^merge/(?P<tag1_id>\d+)/(?P<tag2_id>\d+)/$',
        tag_merge),


    # CONFIRMED TAG
    url(r'^confirmed/(?P<game_id>\d+)/$',
        confirmed_tags_of_game),
    url(r'^confirm/(?P<tag_id>\d+)/(?P<game_id>\d+)/$',
        confirm_tag_staff),
    url(r'^unconfirm_nintendo/(?P<tag_id>\d+)/(?P<game_id>\d+)/$',
        unconfirm_tag_nintendo),


    # VOTE FOR TAG
    url(r'^voted/(?P<game_code>[A-Z0-9]{5})/$',
        voted_tags_of_game),
    url(r'^vote/(?P<tag_id>\d+)/(?P<game_code>[A-Z0-9]{5})/$',
        vote_tag),


    # SUGGESTED TAG
    url(r'^suggested/unconfirmed/all/$',
        all_unconfirmed_suggested_tags),
]
