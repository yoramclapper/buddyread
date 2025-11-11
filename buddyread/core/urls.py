from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("profiel/", views.change_auth, name="change_auth")
]