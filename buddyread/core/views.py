from django.shortcuts import redirect, render
from books.models import BookClubMembers, BookClub


def index(request):
    membership_qs = BookClubMembers.objects.filter(member=request.user)
    membership_count = membership_qs.count()
    if membership_count == 1:
        membership = membership_qs.first()
        return redirect("books", club=membership.book_club.slug)

    if membership_count > 1:
        return redirect("choose_club")

    return redirect("add_club")
