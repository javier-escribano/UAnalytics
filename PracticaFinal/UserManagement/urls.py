from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("register", views.register_request, name="register"),
	path("login", views.login_request, name="login"),
	path("logout", views.logout_request, name= "logout"),
	path("myaccount", views.myaccount, name= "myaccount"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)