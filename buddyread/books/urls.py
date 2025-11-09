from django.urls import path

from . import views

urlpatterns = [
    path("nieuw/", views.add_club, name="add_club"),
    path("<slug:club>/", views.books, name="books"),
    path("<slug:club>/add/boek/", views.add_book, name="add_book"),
    path("review/<int:book_pk>/", views.review, name="review"),
]