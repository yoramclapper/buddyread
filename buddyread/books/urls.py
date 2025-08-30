from django.urls import path

from . import views

urlpatterns = [
    path("", views.books, name="books"),
    path("add/", views.add_book, name="add_book"),
    path("review/<int:book_pk>/", views.review, name="review"),
]