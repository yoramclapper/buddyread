from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Book, Review
from .forms import BookForm, ReviewForm

@login_required
def books(request):
    book_qs = Book.objects.order_by("-creation_date")
    context = {"books": book_qs}
    return render(request, "books/book_list.html", context)


@login_required
def add_book(request):
    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            author = form.cleaned_data['author']
            Book.objects.create(
                title=title,
                author=author,
                selected_by=request.user,
            )
            return redirect('books')
    else:
        form = BookForm()
    context = {'form': form}
    return render(request, "books/add_book.html", context)


@login_required
def review(request, book_pk):
    book = get_object_or_404(Book, pk=book_pk)
    review = Review.objects.filter(user=request.user, book=book).first()
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            score = form.cleaned_data['score']
            comment = form.cleaned_data['comment']
            if review is None:
                Review.objects.create(
                    user=request.user,
                    book=book,
                    score=score,
                    comment=comment
                )
            else:
                review.score=score
                review.comment=comment
                review.save()
            return redirect('books')
    else:
        if review is None:
            form = ReviewForm()
        else:
            initial_data = {'score': review.score, 'comment': review.comment}
            form = ReviewForm(initial=initial_data)
    context = {'book': book, 'form': form}
    return render(request, "books/review_form.html", context)