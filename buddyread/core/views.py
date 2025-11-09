from django.shortcuts import redirect
from books.models import BookClubMembers, BookClub

def index(request):
    membership_qs = BookClubMembers.objects.filter(member=request.user)
    membership_count = membership_qs.count()
    if membership_count == 1:
        membership = membership_qs.first()
        return redirect("books", club=membership.book_club)

    if nr_clubs > 1:
        membership = membership_qs.first()
        return redirect("books", club=membership.book_club)

    return redirect("add_club")
