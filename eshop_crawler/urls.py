from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/classification/', include('classification.urls.urls')),
    path('api/games/', include('games.urls.urls')),
    path('api/user/', include('users.urls')),
]
