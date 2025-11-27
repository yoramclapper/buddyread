from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.db.models import Prefetch
from .models import Book, Review, BookClub, BookClubMembers, BookClubBooks, InviteURL
from .forms import BookForm, ReviewForm, BookClubForm, ConfirmDeleteForm, ConfirmModeratorForm, InviteMemberForm
from .decorators import user_is_club_member, user_is_club_mod


@login_required
def add_or_edit_club(request, club=None):
    book_club = None
    form_caption = "Start een nieuwe boekenclub!"

    if club is not None:
        book_club = get_object_or_404(BookClub, slug=club)
        member = get_object_or_404(BookClubMembers, book_club=book_club, member=request.user)

        if not member.is_mod:
            return HttpResponseForbidden(
                f"Geen recht om boekenclub '{book_club.name}' te wijzigen"
            )

        form_caption = "Wijzig boekenclub"

    if request.method == "POST":
        form = BookClubForm(request.POST, instance=book_club)
        if form.is_valid():
            book_club = form.save()

            if club is None:
                BookClubMembers.objects.create(
                    book_club=book_club, member=request.user, is_mod=True
                )

            return redirect("books", club=book_club.slug)

    else:
        form = BookClubForm(instance=book_club)

    return render(request, "books/generic_form.html", {
        'form': form,
        'form_caption': form_caption
    })


@login_required
@user_is_club_mod
def delete_club(request, club):
    book_club = get_object_or_404(BookClub, slug=club)
    if request.method == "POST":
        form = ConfirmDeleteForm(request.POST)
        if form.is_valid():
            book_club.delete()
            return redirect('club_overview')
    else:
        form = ConfirmDeleteForm()
    context = {
        'form': form,
        'form_caption': f"Verwijder boekenclub '{book_club.name}' en alle gerelateerde gegevens",
    }
    return render(request, "books/generic_form.html", context)


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
    context = {
        'form': form,
        'form_caption': f"Voeg een boek toe aan {book_club.name}",
        'club': book_club.name
    }
    return render(request, "books/generic_form.html", context)


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

@login_required
def club_overview(request):
    book_clubs = BookClubMembers.objects.filter(member=request.user)
    context = {'book_clubs': book_clubs}
    return render(request, "books/club_overview.html", context)


@login_required
@user_is_club_mod
def club_custom_admin(request, club):
    book_club = get_object_or_404(BookClub, slug=club)
    context = {
        "book_club": book_club,
        "members": BookClubMembers.objects.filter(book_club=book_club),
        "club_books": BookClubBooks.objects.filter(book_club=book_club)
    }
    return render(request, "books/club_custom_admin.html", context)


@login_required
@user_is_club_mod
def delete_club_member(request, club, member_pk):
    book_club = get_object_or_404(BookClub, slug=club)
    club_member = get_object_or_404(BookClubMembers, book_club=book_club, pk=member_pk)
    if request.method == "POST":
        form = ConfirmDeleteForm(request.POST)
        if form.is_valid():
            club_member.delete()
            return redirect("club_custom_admin", club=book_club.slug)
    else:
        if club_member.is_mod:
            return redirect("club_custom_admin", club=book_club.slug)
        form = ConfirmDeleteForm()
    context = {
        'form': form,
        'form_caption': f"Verwijder lid '{club_member.member.username}' en alle gerelateerde gegevens uit '{book_club.name}'",
    }
    return render(request, "books/generic_form.html", context)


@login_required
@user_is_club_mod
def delete_club_book(request, club, book_pk):
    book_club = get_object_or_404(BookClub, slug=club)
    club_book = get_object_or_404(BookClubBooks, book_club=book_club, pk=book_pk)
    if request.method == "POST":
        form = ConfirmDeleteForm(request.POST)
        if form.is_valid():
            club_book.delete()
            return redirect("club_custom_admin", club=book_club.slug)
    else:
        form = ConfirmDeleteForm()
    context = {
        'form': form,
        'form_caption': f"Verwijder boek '{club_book.book.title}' en alle gerelateerde gegevens uit '{book_club.name}'",
    }
    return render(request, "books/generic_form.html", context)


@login_required
@user_is_club_mod
def grant_mod_perm(request, club, member_pk):
    book_club = get_object_or_404(BookClub, slug=club)
    club_member = get_object_or_404(BookClubMembers, book_club=book_club, pk=member_pk)
    if request.method == "POST":
        form = ConfirmModeratorForm(request.POST)
        if form.is_valid():
            club_member.is_mod = True
            club_member.save()
            return redirect("club_custom_admin", club=book_club.slug)
    else:
        if club_member.is_mod:
            return redirect("club_custom_admin", club=book_club.slug)
        form = ConfirmModeratorForm()
    context = {
        'form': form,
        'form_caption': f"Geef het lid '{club_member.member.username}' recht om '{book_club.name}' te beheren",
    }
    return render(request, "books/generic_form.html", context)


@login_required
@user_is_club_mod
def invite_member(request, club):
    book_club = get_object_or_404(BookClub, slug=club)
    invite_url = InviteURL.objects.create(book_club=book_club)
    url = reverse('sign_up', kwargs={'url_uuid': invite_url.uuid})
    context = {
        'book_club': book_club,
        'invite_url': request.build_absolute_uri(url)
    }
    return render(request, "books/invite_member.html", context)


def sign_up(request, url_uuid):
    invite_url = InviteURL.objects.get(uuid=url_uuid)
    book_club = get_object_or_404(BookClub, slug=invite_url.book_club.slug)

    if invite_url.accepted or invite_url.is_expired():
        return HttpResponseForbidden("Uitnodiging is verlopen")

    if request.method == "POST":
        form = InviteMemberForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            new_user = get_user_model().objects.create_user(username=username, password=password)
            BookClubMembers.objects.create(book_club=book_club, member=new_user)
            invite_url.accepted=True
            invite_url.save()
            return redirect("index")

    else:
        form = InviteMemberForm()

    context = {
        'form': form,
        'form_caption': f"Wordt lid bij boekenclub: {book_club.name}",
    }
    return render(request, "books/generic_form.html", context)
