from django.urls import path

from . import views

urlpatterns = [
    path("", views.books, name="books"),
    path("review/<int:book_pk>/", views.review, name="review"),
]