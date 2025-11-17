from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Prefetch
from .models import Book, Review, BookClub, BookClubMembers, BookClubBooks
from .forms import BookForm, ReviewForm, BookClubForm
from .decorators import user_is_club_member


@login_required
def add_club(request):
    if request.method == "POST":
        form = BookClubForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            book_club = BookClub.objects.create(name=name)
            BookClubMembers.objects.create(book_club=book_club, member=request.user)
            return redirect("books", club=book_club.slug)
    else:
        form = BookClubForm()
    context = {'form': form}
    return render(request, "books/add_club.html", context)


@login_required
def choose_club(request):
    book_clubs = [
        m.book_club
        for m in BookClubMembers.objects.filter(member=request.user)
    ]
    context = {'book_clubs': book_clubs}
    return render(request, "books/choose_club.html", context)


@login_required
@user_is_club_member
def books(request, club):
    book_club = get_object_or_404(BookClub, slug=club)
    book_club_books = BookClubBooks.objects.filter(book_club=book_club)
    book_clubs = [
        m.book_club
        for m in BookClubMembers.objects.filter(member=request.user)
        if m.book_club != book_club
    ]

    book_qs = book_club_books.select_related("book").prefetch_related(
            Prefetch(
                "book__review_set",
                queryset=Review.objects.filter(
                    user__in=book_club.bookclubmembers_set.values("member")
                )
            )
        ).order_by('-date_added')
    context = {"books": book_qs, "club": book_club, "book_clubs": book_clubs}
    return render(request, "books/book_list.html", context)


@login_required
@user_is_club_member
def add_book(request, club):
    book_club = get_object_or_404(BookClub, slug=club)
    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            author = form.cleaned_data['author']
            book, created = Book.objects.get_or_create(
                title=title,
                author=author,
            )
            BookClubBooks.objects.create(
                book_club=book_club,
                book=book,
                selected_by=request.user,
            )
            return redirect('books', club=book_club.slug)
    else:
        form = BookForm()
    context = {'form': form, 'club': book_club.name}
    return render(request, "books/add_book.html", context)


@login_required
@user_is_club_member
def review(request, club, book_pk):
    book = get_object_or_404(Book, pk=book_pk)
    book_club = get_object_or_404(BookClub, slug=club)
    review_selected = Review.objects.filter(user=request.user, book=book).first()
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            score = form.cleaned_data['score']
            comment = form.cleaned_data['comment']
            if review_selected is None:
                Review.objects.create(
                    user=request.user,
                    book=book,
                    score=score,
                    comment=comment
                )
            else:
                review_selected.score=score
                review_selected.comment=comment
                review_selected.save()
            return redirect('books', club=book_club.slug)
    else:
        if review_selected is None:
            form = ReviewForm()
        else:
            initial_data = {
                'score': review_selected.score,
                'comment': review_selected.comment
            }
            form = ReviewForm(initial=initial_data)
    context = {'book': book, 'form': form}
    return render(request, "books/review_form.html", context)
