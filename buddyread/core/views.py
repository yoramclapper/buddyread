from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from core.forms import ChangeAuthForm
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

def change_auth(request):
    user = request.user
    if request.method == 'POST':
        form = ChangeAuthForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            current_password = form.cleaned_data['current_password']
            new_password = form.cleaned_data['new_password']
            new_password_repeat = form.cleaned_data['new_password_repeat']

            if not user.check_password(current_password):
                form.add_error('current_password', 'Huidig wachtwoord is incorrect')

            elif new_password != new_password_repeat:
                form.add_error('new_password', 'Het nieuwe wachtwoord en de herhaling komen niet overeen')
                form.add_error('new_password_repeat', '')

            else:
                user.username = username
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                return redirect("/")

    else:
        form = ChangeAuthForm(initial={'username': user.username})

    return render(request, 'core/profile.html', {'form': form})

