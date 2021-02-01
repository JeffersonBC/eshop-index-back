from django.conf.urls import url

from ..api.review import (
    review,
    review_vote,
    all_reviews,
)


urlpatterns = [
    url(r'^(?P<game_code>[A-Z0-9]{5})/$',
        review),

    url(r'^vote/(?P<review_id>\d+)/$',
        review_vote),

    url(r'^all/(?P<game_code>[A-Z0-9]{5})/$',
        all_reviews),

]
