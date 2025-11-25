from django.urls import path

from . import views

urlpatterns = [
    path("nieuwe/", views.add_or_edit_club, name="add_club"),
    path("keuze/", views.choose_club, name="choose_club"),
    path("beheer/", views.club_overview, name="club_overview"),
    path("beheer/<slug:club>/", views.club_custom_admin, name="club_custom_admin"),
    path("beheer/<slug:club>/wijzig/", views.add_or_edit_club, name="edit_club"),
    path("<slug:club>/", views.books, name="books"),
    path("<slug:club>/add/boek/", views.add_book, name="add_book"),
    path("<slug:club>/review/<int:book_pk>/", views.review, name="review"),
]