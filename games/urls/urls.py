from django.conf.urls import url, include


urlpatterns = [
    url('', include('games.urls.admin')),
    url('', include('games.urls.games')),
    url('', include('games.urls.home_lists')),
    url('', include('games.urls.queries')),

    url('media/', include('games.urls.media')),
    url('price/', include('games.urls.price')),
]
