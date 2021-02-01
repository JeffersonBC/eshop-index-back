from django.conf.urls import url, include

urlpatterns = [
    url(r'^alike/', include('classification.urls.alike')),
    url(r'^recomendation/', include('classification.urls.recomendation')),
    url(r'^review/', include('classification.urls.review')),
    url(r'^tag/', include('classification.urls.tag')),
    url(r'^wishlist/', include('classification.urls.wishlist')),
]
