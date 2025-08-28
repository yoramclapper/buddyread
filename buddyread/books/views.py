from django.shortcuts import render
from .models import Book

def books(request):
    book_qs = Book.objects.order_by("-creation_date")
    context = {"books": book_qs}
    return render(request, "books/book_list.html", context)