from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
	path('',views.index, name='index'),
	path('twitch',views.index_t, name='twitch'),
	path('youtube',views.index_youtube, name='index_Y'),
	path('twitter',views.index_twitter, name='index_T'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
