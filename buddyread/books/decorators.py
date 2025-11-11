from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from functools import wraps
from .models import BookClub, BookClubMembers

def user_is_club_member(view_func):
    @wraps(view_func)
    def wrap(request, club, *args, **kwargs):
        book_club = get_object_or_404(BookClub, slug=club)
        member = request.user
        book_club_members_qs = BookClubMembers.objects.filter(
            book_club=book_club,
            member=member
        )
        if not book_club_members_qs.exists():
            return HttpResponseForbidden("Toegang geweigerd voor de geselecteerde boeken club")
        return view_func(request, club, *args, **kwargs)
    return wrap
