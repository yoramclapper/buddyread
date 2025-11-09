from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Book, Review, BookClub, BookClubMembers, BookClubBooks
from .forms import BookForm, ReviewForm, BookClubForm

@login_required
def books(request, club):
    book_club = BookClub.objects.get(slug=club)
    book_club_books = BookClubBooks.objects.filter(book_club=book_club)
    if not book_club_books.exists():
        return redirect("add_book", club=club)

    book_qs = book_club_books.first().get_books()
    context = {"books": book_qs, "club": club}
    return render(request, "books/book_list.html", context)


@login_required
def add_book(request, club):
    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            author = form.cleaned_data['author']
            book = Book.objects.create(
                title=title,
                author=author,
                selected_by=request.user,
            )
            book_club = BookClub.objects.get(slug=club)
            BookClubBooks.objects.create(
                book_club=book_club,
                book=book
            )
            return redirect('books', club=club)
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


@login_required
def add_club(request):
    if request.method == "POST":
        form = BookClubForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            book_club = BookClub.objects.create(name=name)
            BookClubMembers.objects.create(book_club=book_club, member=request.user)
            return redirect('/')
    else:
        form = BookClubForm()
    context = {'form': form}
    return render(request, "books/add_club.html", context)