from django.urls import path

from . import views

urlpatterns = [
    path("nieuwe/", views.add_or_edit_club, name="add_club"),
    path("keuze/", views.choose_club, name="choose_club"),
    path("uitnodiging/<str:url_uuid>/", views.sign_up, name="sign_up"),
    path("beheer/", views.club_overview, name="club_overview"),
    path("beheer/<slug:club>/", views.club_custom_admin, name="club_custom_admin"),
    path("beheer/<slug:club>/wijzig/", views.add_or_edit_club, name="edit_club"),
    path("beheer/<slug:club>/verwijder/", views.delete_club, name="delete_club"),
    path("beheer/<slug:club>/verwijder/lid/<int:member_pk>", views.delete_club_member, name="delete_club_member"),
    path("beheer/<slug:club>/verwijder/boek/<int:book_pk>", views.delete_club_book, name="delete_club_book"),
    path("beheer/<slug:club>/rechten/lid/<int:member_pk>", views.grant_mod_perm, name="grant_mod_perm"),
    path("beheer/<slug:club>/uitnodigen/lid/", views.invite_member, name="invite_member"),
    path("<slug:club>/", views.books, name="books"),
    path("<slug:club>/add/boek/", views.add_book, name="add_book"),
    path("<slug:club>/review/<int:book_pk>/", views.review, name="review"),
]