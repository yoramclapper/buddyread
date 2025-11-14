from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from core.forms import ChangeAuthForm
from books.models import BookClubMembers, BookClub


@login_required
def index(request):
    membership_qs = BookClubMembers.objects.filter(member=request.user)
    membership_count = membership_qs.count()
    if membership_count == 1:
        membership = membership_qs.first()
        return redirect("books", club=membership.book_club.slug)

    if membership_count > 1:
        return redirect("choose_club")

    return redirect("add_club")

@login_required
def change_auth(request):
    user = request.user
    if request.method == 'POST':
        form = ChangeAuthForm(data=request.POST, user=user)
        if form.is_valid():
            user.username = form.cleaned_data['username']
            new_password = form.cleaned_data['new_password']
            if new_password:
                user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)
            return redirect("/")
    else:
        form = ChangeAuthForm(initial={'username': user.username}, user=user)
    return render(request, 'core/profile.html', {'form': form})

