from django.conf.urls import url

from classification.api.wishlist import wishlist, wishlist_item

urlpatterns = [
    url(r'^$',
        wishlist),

    url(r'^(?P<game_code>[A-Z0-9]{5})/$',
        wishlist_item),
]
