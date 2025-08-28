from django.shortcuts import render, get_object_or_404, redirect
from .models import Book, Review
from .forms import ReviewForm


def books(request):
    book_qs = Book.objects.order_by("-creation_date")
    context = {"books": book_qs}
    return render(request, "books/book_list.html", context)


def review(request, book_pk):
    book = get_object_or_404(Book, pk=book_pk)
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('books')
    else:
        form = ReviewForm()
    context = {'book': book, 'form': form}
    return render(request, "books/review_form.html", context)