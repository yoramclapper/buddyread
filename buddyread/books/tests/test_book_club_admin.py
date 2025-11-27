from datetime import datetime, timedelta
import pytest
from pytest_django.asserts import assertRedirects
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils import timezone
import books.models as books_models
import books.forms as books_forms


def test_url_to_visit_club_overview_exists():
    url_name = 'club_overview'
    try:
        reverse(url_name)
    except Exception as exc:
        pytest.fail(str(exc))


def test_visit_club_overview_requires_login(client):
    url_name = 'club_overview'
    response = client.get(reverse(url_name))
    assert response.status_code == 302
    assert f"/accounts/login/?next=" in response.url


@pytest.mark.django_db
def test_visit_club_overview_is_ok(client, django_user_model):
    username = 'user'
    password = 'pwd'
    django_user_model.objects.create_user(username=username, password=password)
    client.login(username=username, password=password)
    url_name = 'club_overview'

    response = client.get(reverse(url_name))
    assert response.status_code == 200
    assert 'books/club_overview.html' in [t.name for t in response.templates]


@pytest.mark.django_db
def test_club_overview_shows_book_clubs_of_member(client, django_user_model):
    username = 'user'
    password = 'pwd'
    user = django_user_model.objects.create_user(username=username, password=password)
    book_club_1 = books_models.BookClub.objects.create(name="Bookclub 1")
    books_models.BookClubMembers.objects.create(book_club=book_club_1, member=user)
    book_club_2 = books_models.BookClub.objects.create(name="Bookclub 2")
    books_models.BookClubMembers.objects.create(book_club=book_club_2, member=user)

    user_alt = django_user_model.objects.create_user(username="user_alt", password=password)
    book_club_alt = books_models.BookClub.objects.create(name="Bookclub (alternative)")
    books_models.BookClubMembers.objects.create(book_club=book_club_alt, member=user_alt)

    client.login(username=username, password=password)
    url_name = 'club_overview'

    response = client.get(reverse(url_name))
    context = response.context[-1]
    assert "book_clubs" in context

    book_clubs_of_user = context["book_clubs"]
    assert book_clubs_of_user.count() == 2

    book_clubs = [b.book_club for b in book_clubs_of_user]
    assert book_club_1 in book_clubs
    assert book_club_2 in book_clubs


@pytest.mark.django_db
def test_url_to_visit_club_custom_admin_exists():
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    url_name = 'club_custom_admin'
    try:
        reverse(url_name, kwargs={"club": book_club.slug})
    except Exception as exc:
        pytest.fail(str(exc))


@pytest.mark.django_db
def test_visit_club_custom_admin_requires_login(client):
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    url_name = 'club_custom_admin'
    response = client.get(reverse(url_name, kwargs={"club": book_club.slug}))
    assert response.status_code == 302
    assert f"/accounts/login/?next=" in response.url


@pytest.mark.django_db
def test_visit_club_custom_admin_requires_mod_perm(client, django_user_model):
    username = 'user'
    password = 'pwd'
    user = django_user_model.objects.create_user(username=username, password=password)
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    books_models.BookClubMembers.objects.create(book_club=book_club, member=user, is_mod=False)
    url_name = 'club_custom_admin'
    client.login(username=username, password=password)
    response = client.get(reverse(url_name, kwargs={"club": book_club.slug}))
    assert response.status_code == 403


@pytest.mark.django_db
def test_visit_club_custom_admin_as_mod_is_ok(client, django_user_model):
    username = 'user'
    password = 'pwd'
    user = django_user_model.objects.create_user(username=username, password=password)
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    books_models.BookClubMembers.objects.create(book_club=book_club, member=user, is_mod=True)
    url_name = 'club_custom_admin'
    client.login(username=username, password=password)
    response = client.get(reverse(url_name, kwargs={"club": book_club.slug}))
    assert response.status_code == 200


@pytest.mark.django_db
def test_club_custom_admin_context_contains_book_club(client, django_user_model):
    username = 'user'
    password = 'pwd'
    member_mod = django_user_model.objects.create_user(username=username, password=password)
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    books_models.BookClubMembers.objects.create(book_club=book_club, member=member_mod, is_mod=True)

    url_name = 'club_custom_admin'
    client.login(username=username, password=password)
    response = client.get(reverse(url_name, kwargs={"club": book_club.slug}))

    context = response.context[-1]
    assert "book_club" in context
    assert context["book_club"] == book_club


@pytest.mark.django_db
def test_club_custom_admin_context_contains_club_members(client, django_user_model):
    username = 'user'
    password = 'pwd'
    member_mod = django_user_model.objects.create_user(username=username, password=password)
    member_other = django_user_model.objects.create_user(username="member", password=password)
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    books_models.BookClubMembers.objects.create(book_club=book_club, member=member_mod, is_mod=True)
    books_models.BookClubMembers.objects.create(book_club=book_club, member=member_other, is_mod=False)

    member_alt = django_user_model.objects.create_user(username="member_alt", password=password)
    book_club_alt = books_models.BookClub.objects.create(name="Bookclub (alternative)")
    books_models.BookClubMembers.objects.create(book_club=book_club_alt, member=member_alt, is_mod=True)

    url_name = 'club_custom_admin'
    client.login(username=username, password=password)
    response = client.get(reverse(url_name, kwargs={"club": book_club.slug}))

    context = response.context[-1]
    assert "members" in context

    members = [m.member for m in context["members"]]
    assert len(members) == 2
    assert member_mod in members
    assert member_other in members


@pytest.mark.django_db
def test_club_custom_admin_context_contains_club_books(client, django_user_model):
    username = 'user'
    password = 'pwd'
    user = django_user_model.objects.create_user(username=username, password=password)
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    books_models.BookClubMembers.objects.create(book_club=book_club, member=user, is_mod=True)
    book_1 = books_models.Book.objects.create(title="Book 1", author="Author 1")
    book_2 = books_models.Book.objects.create(title="Book 2", author="Author 2")
    books_models.BookClubBooks.objects.create(book_club=book_club, book=book_1, selected_by=user)
    books_models.BookClubBooks.objects.create(book_club=book_club, book=book_2, selected_by=user)

    user_alt = django_user_model.objects.create_user(username="user_alt", password=password)
    book_club_alt = books_models.BookClub.objects.create(name="Bookclub (alternative)")
    book_alt = books_models.Book.objects.create(title="Book (alternative)", author="Author (alternative)")
    books_models.BookClubBooks.objects.create(book_club=book_club_alt, book=book_alt, selected_by=user_alt)

    url_name = 'club_custom_admin'
    client.login(username=username, password=password)
    response = client.get(reverse(url_name, kwargs={"club": book_club.slug}))

    context = response.context[-1]
    assert "club_books" in context

    club_books = [cb.book for cb in context["club_books"]]
    assert len(club_books) == 2
    assert book_1 in club_books
    assert book_2 in club_books


@pytest.mark.django_db
def test_url_to_edit_club_exists():
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    url_name = 'edit_club'
    try:
        reverse(url_name, kwargs={"club": book_club.slug})
    except Exception as exc:
        pytest.fail(str(exc))


@pytest.mark.django_db
def test_edit_club_requires_login(client):
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    url_name = 'edit_club'
    response = client.get(reverse(url_name, kwargs={"club": book_club.slug}))
    assert response.status_code == 302
    assert f"/accounts/login/?next=" in response.url


@pytest.mark.django_db
def test_edit_club_requires_mod_perm(client, django_user_model):
    username = 'user'
    password = 'pwd'
    user = django_user_model.objects.create_user(username=username, password=password)
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    books_models.BookClubMembers.objects.create(book_club=book_club, member=user, is_mod=False)
    url_name = 'edit_club'
    client.login(username=username, password=password)
    response = client.get(reverse(url_name, kwargs={"club": book_club.slug}))
    assert response.status_code == 403


@pytest.mark.django_db
def test_visit_edit_club_as_mod_is_ok(client, django_user_model):
    username = 'user'
    password = 'pwd'
    user = django_user_model.objects.create_user(username=username, password=password)
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    books_models.BookClubMembers.objects.create(book_club=book_club, member=user, is_mod=True)
    url_name = 'edit_club'
    client.login(username=username, password=password)
    response = client.get(reverse(url_name, kwargs={"club": book_club.slug}))
    assert response.status_code == 200


@pytest.mark.django_db
def test_edit_club_shows_correct_form_with_initial_data(client, django_user_model):
    username = 'user'
    password = 'pwd'
    user = django_user_model.objects.create_user(username=username, password=password)
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    books_models.BookClubMembers.objects.create(book_club=book_club, member=user, is_mod=True)
    url_name = 'edit_club'
    client.login(username=username, password=password)
    response = client.get(reverse(url_name, kwargs={"club": book_club.slug}))
    context = response.context[-1]

    assert 'form' in context

    form = response.context['form']
    assert isinstance(form, books_forms.BookClubForm)

    assert 'name' in form.initial
    assert form.initial['name'] == book_club.name


@pytest.mark.django_db
def test_edit_club_is_ok(client, django_user_model):
    username = 'user'
    password = 'pwd'
    user = django_user_model.objects.create_user(username=username, password=password)
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    books_models.BookClubMembers.objects.create(book_club=book_club, member=user, is_mod=True)
    url_name = 'edit_club'
    client.login(username=username, password=password)

    book_club_name_edit = "Bookclub edit"
    response = client.post(
        reverse(url_name, kwargs={"club": book_club.slug}),
        data={"name": book_club_name_edit}
    )

    book_club = books_models.BookClub.objects.get(pk=book_club.pk)
    assert book_club.name == book_club_name_edit

    assertRedirects(
        response=response,
        expected_url=reverse("books", kwargs={"club": book_club.slug}),
        status_code=302
    )


@pytest.mark.django_db
def test_url_to_delete_club_exists():
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    url_name = 'delete_club'
    try:
        reverse(url_name, kwargs={"club": book_club.slug})
    except Exception as exc:
        pytest.fail(str(exc))


@pytest.mark.django_db
def test_delete_club_requires_login(client):
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    url_name = 'delete_club'
    response = client.get(reverse(url_name, kwargs={"club": book_club.slug}))
    assert response.status_code == 302
    assert f"/accounts/login/?next=" in response.url


@pytest.mark.django_db
def test_delete_club_requires_mod_perm(client, django_user_model):
    username = 'user'
    password = 'pwd'
    user = django_user_model.objects.create_user(username=username, password=password)
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    books_models.BookClubMembers.objects.create(book_club=book_club, member=user, is_mod=False)
    url_name = 'delete_club'
    client.login(username=username, password=password)
    response = client.get(reverse(url_name, kwargs={"club": book_club.slug}))
    assert response.status_code == 403


@pytest.mark.django_db
def test_visit_delete_club_as_mod_is_ok(client, django_user_model):
    username = 'user'
    password = 'pwd'
    user = django_user_model.objects.create_user(username=username, password=password)
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    books_models.BookClubMembers.objects.create(book_club=book_club, member=user, is_mod=True)
    url_name = 'delete_club'
    client.login(username=username, password=password)
    response = client.get(reverse(url_name, kwargs={"club": book_club.slug}))
    assert response.status_code == 200


@pytest.mark.django_db
def test_delete_club_shows_correct_form(client, django_user_model):
    username = 'user'
    password = 'pwd'
    user = django_user_model.objects.create_user(username=username, password=password)
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    books_models.BookClubMembers.objects.create(book_club=book_club, member=user, is_mod=True)
    url_name = 'delete_club'
    client.login(username=username, password=password)
    response = client.get(reverse(url_name, kwargs={"club": book_club.slug}))
    context = response.context[-1]

    assert 'form' in context

    form = response.context['form']
    assert isinstance(form, books_forms.ConfirmDeleteForm)


@pytest.mark.django_db
def test_delete_club_is_ok(client, django_user_model):
    username = 'user'
    password = 'pwd'
    member_mod = django_user_model.objects.create_user(username=username, password=password)
    member_other = django_user_model.objects.create_user(username="member", password=password)
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    club_member_mod = books_models.BookClubMembers.objects.create(book_club=book_club, member=member_mod, is_mod=True)
    club_member = books_models.BookClubMembers.objects.create(book_club=book_club, member=member_other, is_mod=False)
    book_1 = books_models.Book.objects.create(title="Book 1", author="Author 1")
    book_2 = books_models.Book.objects.create(title="Book 2", author="Author 2")
    club_book_1 = books_models.BookClubBooks.objects.create(book_club=book_club, book=book_1, selected_by=member_mod)
    club_book_2 = books_models.BookClubBooks.objects.create(book_club=book_club, book=book_2, selected_by=member_other)

    member_alt = django_user_model.objects.create_user(username="member_alt", password=password)
    book_club_alt = books_models.BookClub.objects.create(name="Bookclub (alternative)")
    club_member_alt = books_models.BookClubMembers.objects.create(book_club=book_club_alt, member=member_alt, is_mod=True)
    book_alt = books_models.Book.objects.create(title="Book (alternative)", author="Author (alternative)")
    club_book_alt = books_models.BookClubBooks.objects.create(book_club=book_club_alt, book=book_alt, selected_by=member_alt)

    url_name = 'delete_club'
    client.login(username=username, password=password)

    response = client.post(
        reverse(url_name, kwargs={"club": book_club.slug}),
        data={"confirm": True}
    )

    assert not books_models.BookClub.objects.filter(pk=book_club.pk).exists()

    assert django_user_model.objects.filter(pk=member_mod.pk).exists()
    assert django_user_model.objects.filter(pk=member_other.pk).exists()
    assert not books_models.BookClubMembers.objects.filter(pk=club_member_mod.pk).exists()
    assert not books_models.BookClubMembers.objects.filter(pk=club_member.pk).exists()

    assert books_models.Book.objects.filter(pk=book_1.pk).exists()
    assert books_models.Book.objects.filter(pk=book_2.pk).exists()
    assert not books_models.BookClubBooks.objects.filter(pk=club_book_1.pk).exists()
    assert not books_models.BookClubBooks.objects.filter(pk=club_book_2.pk).exists()

    assert books_models.BookClubMembers.objects.filter(pk=club_member_alt.pk).exists()
    assert books_models.BookClub.objects.filter(pk=book_club_alt.pk).exists()
    assert books_models.Book.objects.filter(pk=book_alt.pk).exists()
    assert books_models.BookClubBooks.objects.filter(pk=club_book_alt.pk).exists()

    assertRedirects(
        response=response,
        expected_url=reverse("club_overview"),
        status_code=302
    )


@pytest.mark.django_db
def test_url_to_delete_club_member_exists():
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    url_name = 'delete_club_member'
    try:
        reverse(url_name, kwargs={"club": book_club.slug, "member_pk": 1})
    except Exception as exc:
        pytest.fail(str(exc))


@pytest.mark.django_db
def test_delete_club_member_requires_login(client):
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    url_name = 'delete_club_member'
    response = client.get(reverse(url_name, kwargs={"club": book_club.slug, "member_pk": 1}))
    assert response.status_code == 302
    assert f"/accounts/login/?next=" in response.url


@pytest.mark.django_db
def test_delete_club_member_requires_mod_perm(client, django_user_model):
    username = 'user'
    password = 'pwd'
    user = django_user_model.objects.create_user(username=username, password=password)
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    books_models.BookClubMembers.objects.create(book_club=book_club, member=user, is_mod=False)
    url_name = 'delete_club_member'
    client.login(username=username, password=password)
    response = client.get(reverse(url_name, kwargs={"club": book_club.slug, "member_pk": 1}))
    assert response.status_code == 403


@pytest.mark.django_db
def test_visit_delete_club_member_of_other_member_as_mod_is_ok(client, django_user_model):
    username = 'user'
    password = 'pwd'
    user = django_user_model.objects.create_user(username=username, password=password)
    user_2 = django_user_model.objects.create_user(username="user2", password=password)
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    books_models.BookClubMembers.objects.create(book_club=book_club, member=user, is_mod=True)
    member = books_models.BookClubMembers.objects.create(book_club=book_club, member=user_2, is_mod=False)
    url_name = 'delete_club_member'
    client.login(username=username, password=password)
    response = client.get(reverse(url_name, kwargs={"club": book_club.slug, "member_pk": member.pk}))
    assert response.status_code == 200


@pytest.mark.django_db
def test_visit_delete_club_member_of_other_mod_redirects(client, django_user_model):
    username = 'user'
    password = 'pwd'
    user = django_user_model.objects.create_user(username=username, password=password)
    user_2 = django_user_model.objects.create_user(username="user2", password=password)
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    books_models.BookClubMembers.objects.create(book_club=book_club, member=user, is_mod=True)
    member = books_models.BookClubMembers.objects.create(book_club=book_club, member=user_2, is_mod=True)
    url_name = 'delete_club_member'
    client.login(username=username, password=password)
    response = client.get(reverse(url_name, kwargs={"club": book_club.slug, "member_pk": member.pk}))
    assertRedirects(
        response=response,
        expected_url=reverse("club_custom_admin", kwargs={"club": book_club.slug}),
        status_code=302
    )


@pytest.mark.django_db
def test_delete_club_member_shows_correct_form(client, django_user_model):
    username = 'user'
    password = 'pwd'
    user = django_user_model.objects.create_user(username=username, password=password)
    user_2 = django_user_model.objects.create_user(username="user2", password=password)
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    books_models.BookClubMembers.objects.create(book_club=book_club, member=user, is_mod=True)
    member = books_models.BookClubMembers.objects.create(book_club=book_club, member=user_2, is_mod=False)
    url_name = 'delete_club_member'
    client.login(username=username, password=password)
    response = client.get(reverse(url_name, kwargs={"club": book_club.slug, "member_pk": member.pk}))
    context = response.context[-1]

    assert 'form' in context

    form = response.context['form']
    assert isinstance(form, books_forms.ConfirmDeleteForm)


@pytest.mark.django_db
def test_delete_club_member_is_ok(client, django_user_model):
    username = 'user'
    password = 'pwd'
    user = django_user_model.objects.create_user(username=username, password=password)
    user_2 = django_user_model.objects.create_user(username="user2", password=password)
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    books_models.BookClubMembers.objects.create(book_club=book_club, member=user, is_mod=True)
    member = books_models.BookClubMembers.objects.create(book_club=book_club, member=user_2, is_mod=False)

    url_name = 'delete_club_member'
    client.login(username=username, password=password)

    response = client.post(
        reverse(url_name, kwargs={"club": book_club.slug, "member_pk": member.pk}),
        data={"confirm": True}
    )

    assert django_user_model.objects.filter(pk=user_2.pk).exists()
    assert not books_models.BookClubMembers.objects.filter(pk=member.pk).exists()

    assertRedirects(
        response=response,
        expected_url=reverse("club_custom_admin", kwargs={"club": book_club.slug}),
        status_code=302
    )


@pytest.mark.django_db
def test_url_to_delete_club_book_exists():
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    url_name = 'delete_club_book'
    try:
        reverse(url_name, kwargs={"club": book_club.slug, "book_pk": 1})
    except Exception as exc:
        pytest.fail(str(exc))


@pytest.mark.django_db
def test_delete_club_book_requires_login(client):
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    url_name = 'delete_club_book'
    response = client.get(reverse(url_name, kwargs={"club": book_club.slug, "book_pk": 1}))
    assert response.status_code == 302
    assert f"/accounts/login/?next=" in response.url


@pytest.mark.django_db
def test_delete_club_book_requires_mod_perm(client, django_user_model):
    username = 'user'
    password = 'pwd'
    user = django_user_model.objects.create_user(username=username, password=password)
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    books_models.BookClubMembers.objects.create(book_club=book_club, member=user, is_mod=False)
    url_name = 'delete_club_book'
    client.login(username=username, password=password)
    response = client.get(reverse(url_name, kwargs={"club": book_club.slug, "book_pk": 1}))
    assert response.status_code == 403


@pytest.mark.django_db
def test_visit_delete_club_book_as_mod_is_ok(client, django_user_model):
    username = 'user'
    password = 'pwd'
    user = django_user_model.objects.create_user(username=username, password=password)
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    books_models.BookClubMembers.objects.create(book_club=book_club, member=user, is_mod=True)
    book = books_models.Book.objects.create(title="Book", author="Author")
    club_book = books_models.BookClubBooks.objects.create(book_club=book_club, book=book)
    url_name = 'delete_club_book'
    client.login(username=username, password=password)
    response = client.get(reverse(url_name, kwargs={"club": book_club.slug, "book_pk": club_book.pk}))
    assert response.status_code == 200


@pytest.mark.django_db
def test_delete_club_book_shows_correct_form(client, django_user_model):
    username = 'user'
    password = 'pwd'
    user = django_user_model.objects.create_user(username=username, password=password)
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    books_models.BookClubMembers.objects.create(book_club=book_club, member=user, is_mod=True)
    book = books_models.Book.objects.create(title="Book", author="Author")
    club_book = books_models.BookClubBooks.objects.create(book_club=book_club, book=book)
    url_name = 'delete_club_book'
    client.login(username=username, password=password)
    response = client.get(reverse(url_name, kwargs={"club": book_club.slug, "book_pk": club_book.pk}))
    context = response.context[-1]

    assert 'form' in context

    form = response.context['form']
    assert isinstance(form, books_forms.ConfirmDeleteForm)


@pytest.mark.django_db
def test_delete_club_book_is_ok(client, django_user_model):
    username = 'user'
    password = 'pwd'
    user = django_user_model.objects.create_user(username=username, password=password)
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    books_models.BookClubMembers.objects.create(book_club=book_club, member=user, is_mod=True)
    book = books_models.Book.objects.create(title="Book", author="Author")
    club_book = books_models.BookClubBooks.objects.create(book_club=book_club, book=book)

    url_name = 'delete_club_book'
    client.login(username=username, password=password)

    response = client.post(
        reverse(url_name, kwargs={"club": book_club.slug, "book_pk": club_book.pk}),
        data={"confirm": True}
    )

    assert books_models.Book.objects.filter(pk=book.pk).exists()
    assert not books_models.BookClubBooks.objects.filter(pk=club_book.pk).exists()

    assertRedirects(
        response=response,
        expected_url=reverse("club_custom_admin", kwargs={"club": book_club.slug}),
        status_code=302
    )


@pytest.mark.django_db
def test_url_to_grant_mod_perm_exists():
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    url_name = 'grant_mod_perm'
    try:
        reverse(url_name, kwargs={"club": book_club.slug, "member_pk": 1})
    except Exception as exc:
        pytest.fail(str(exc))


@pytest.mark.django_db
def test_grant_mod_perm_requires_login(client):
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    url_name = 'grant_mod_perm'
    response = client.get(reverse(url_name, kwargs={"club": book_club.slug, "member_pk": 1}))
    assert response.status_code == 302
    assert f"/accounts/login/?next=" in response.url


@pytest.mark.django_db
def test_grant_mod_perm_requires_mod_perm(client, django_user_model):
    username = 'user'
    password = 'pwd'
    user = django_user_model.objects.create_user(username=username, password=password)
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    books_models.BookClubMembers.objects.create(book_club=book_club, member=user, is_mod=False)
    url_name = 'grant_mod_perm'
    client.login(username=username, password=password)
    response = client.get(reverse(url_name, kwargs={"club": book_club.slug, "member_pk": 1}))
    assert response.status_code == 403


@pytest.mark.django_db
def test_visit_grant_mod_perm_of_other_member_as_mod_is_ok(client, django_user_model):
    username = 'user'
    password = 'pwd'
    user = django_user_model.objects.create_user(username=username, password=password)
    user_2 = django_user_model.objects.create_user(username="user2", password=password)
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    books_models.BookClubMembers.objects.create(book_club=book_club, member=user, is_mod=True)
    member = books_models.BookClubMembers.objects.create(book_club=book_club, member=user_2, is_mod=False)
    url_name = 'grant_mod_perm'
    client.login(username=username, password=password)
    response = client.get(reverse(url_name, kwargs={"club": book_club.slug, "member_pk": member.pk}))
    assert response.status_code == 200


@pytest.mark.django_db
def test_visit_grant_mod_perm_of_other_mod_redirects(client, django_user_model):
    username = 'user'
    password = 'pwd'
    user = django_user_model.objects.create_user(username=username, password=password)
    user_2 = django_user_model.objects.create_user(username="user2", password=password)
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    books_models.BookClubMembers.objects.create(book_club=book_club, member=user, is_mod=True)
    member = books_models.BookClubMembers.objects.create(book_club=book_club, member=user_2, is_mod=True)
    url_name = 'grant_mod_perm'
    client.login(username=username, password=password)
    response = client.get(reverse(url_name, kwargs={"club": book_club.slug, "member_pk": member.pk}))
    assertRedirects(
        response=response,
        expected_url=reverse("club_custom_admin", kwargs={"club": book_club.slug}),
        status_code=302
    )


@pytest.mark.django_db
def test_grant_mod_perm_shows_correct_form(client, django_user_model):
    username = 'user'
    password = 'pwd'
    user = django_user_model.objects.create_user(username=username, password=password)
    user_2 = django_user_model.objects.create_user(username="user2", password=password)
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    books_models.BookClubMembers.objects.create(book_club=book_club, member=user, is_mod=True)
    member = books_models.BookClubMembers.objects.create(book_club=book_club, member=user_2, is_mod=False)
    url_name = 'grant_mod_perm'
    client.login(username=username, password=password)
    response = client.get(reverse(url_name, kwargs={"club": book_club.slug, "member_pk": member.pk}))
    context = response.context[-1]

    assert 'form' in context

    form = response.context['form']
    assert isinstance(form, books_forms.ConfirmModeratorForm)


@pytest.mark.django_db
def test_grant_mod_perm_is_ok(client, django_user_model):
    username = 'user'
    password = 'pwd'
    user = django_user_model.objects.create_user(username=username, password=password)
    user_2 = django_user_model.objects.create_user(username="user2", password=password)
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    books_models.BookClubMembers.objects.create(book_club=book_club, member=user, is_mod=True)
    member = books_models.BookClubMembers.objects.create(book_club=book_club, member=user_2, is_mod=False)

    url_name = 'grant_mod_perm'
    client.login(username=username, password=password)

    response = client.post(
        reverse(url_name, kwargs={"club": book_club.slug, "member_pk": member.pk}),
        data={"confirm": True}
    )

    member = books_models.BookClubMembers.objects.get(pk=member.pk)
    assert member.is_mod

    assertRedirects(
        response=response,
        expected_url=reverse("club_custom_admin", kwargs={"club": book_club.slug}),
        status_code=302
    )


@pytest.mark.django_db
def test_url_to_invite_member_exists():
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    url_name = 'invite_member'
    try:
        reverse(url_name, kwargs={"club": book_club.slug})
    except Exception as exc:
        pytest.fail(str(exc))


@pytest.mark.django_db
def test_invite_member_requires_login(client):
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    url_name = 'invite_member'
    response = client.get(reverse(url_name, kwargs={"club": book_club.slug}))
    assert response.status_code == 302
    assert f"/accounts/login/?next=" in response.url


@pytest.mark.django_db
def test_invite_member_requires_mod_perm(client, django_user_model):
    username = 'user'
    password = 'pwd'
    user = django_user_model.objects.create_user(username=username, password=password)
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    books_models.BookClubMembers.objects.create(book_club=book_club, member=user, is_mod=False)
    url_name = 'invite_member'
    client.login(username=username, password=password)
    response = client.get(reverse(url_name, kwargs={"club": book_club.slug}))
    assert response.status_code == 403


@pytest.mark.django_db
def test_invite_member_as_mod_is_ok(client, django_user_model):
    username = 'user'
    password = 'pwd'
    user = django_user_model.objects.create_user(username=username, password=password)
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    books_models.BookClubMembers.objects.create(book_club=book_club, member=user, is_mod=True)
    url_name = 'invite_member'
    client.login(username=username, password=password)
    response = client.get(reverse(url_name, kwargs={"club": book_club.slug}))
    assert response.status_code == 200

@pytest.mark.django_db
def test_invite_member_generates_url(client, django_user_model):
    username = 'user'
    password = 'pwd'
    user = django_user_model.objects.create_user(username=username, password=password)
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    books_models.BookClubMembers.objects.create(book_club=book_club, member=user, is_mod=True)
    url_name = 'invite_member'
    client.login(username=username, password=password)

    assert books_models.InviteURL.objects.all().count() == 0

    client.get(reverse(url_name, kwargs={"club": book_club.slug}))
    invite_url_qs = books_models.InviteURL.objects.all()
    assert invite_url_qs.count() == 1

    invite_url = invite_url_qs.first()
    assert invite_url.book_club == book_club


@pytest.mark.django_db
def test_invite_member_contains_correct_context(client, django_user_model):
    username = 'user'
    password = 'pwd'
    user = django_user_model.objects.create_user(username=username, password=password)
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    books_models.BookClubMembers.objects.create(book_club=book_club, member=user, is_mod=True)
    url_name = 'invite_member'
    client.login(username=username, password=password)

    response = client.get(reverse(url_name, kwargs={"club": book_club.slug}))
    invite_url = books_models.InviteURL.objects.all().first()
    context = response.context[-1]
    assert 'book_club' in context
    assert context['book_club'] == book_club
    assert 'invite_url' in context
    assert str(invite_url.uuid) in context['invite_url']


@pytest.mark.django_db
def test_url_to_sign_up_exists():
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    invite_url = books_models.InviteURL.objects.create(book_club=book_club)
    url_name = 'sign_up'
    try:
        reverse(url_name, kwargs={"url_uuid": invite_url.uuid})
    except Exception as exc:
        pytest.fail(str(exc))


@pytest.mark.django_db
def test_visit_sign_up_is_ok(client):
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    invite_url = books_models.InviteURL.objects.create(book_club=book_club)
    url_name = 'sign_up'
    response = client.get(reverse(url_name, kwargs={"url_uuid": invite_url.uuid}))
    assert response.status_code == 200


@pytest.mark.django_db
def test_visit_sign_up_permission_denied_invite_accepted(client):
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    invite_url = books_models.InviteURL.objects.create(book_club=book_club)
    invite_url.accepted = True
    invite_url.save()
    url_name = 'sign_up'
    response = client.get(reverse(url_name, kwargs={"url_uuid": invite_url.uuid}))
    assert response.status_code == 403


@pytest.mark.django_db
def test_model_invite_url_expire_creation_date_more_than_one_day_ago(client):
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    invite_url = books_models.InviteURL.objects.create(book_club=book_club)
    invite_url.creation_date = timezone.now() - timedelta(days=1)
    assert invite_url.is_expired()


@pytest.mark.django_db
def test_model_invite_url_expire_creation_date_less_than_one_day_ago(client):
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    invite_url = books_models.InviteURL.objects.create(book_club=book_club)
    assert not invite_url.is_expired()


@pytest.mark.django_db
def test_visit_sign_up_permission_denied_invite_is_expired(client):
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    invite_url = books_models.InviteURL.objects.create(book_club=book_club)
    invite_url.creation_date = timezone.now() - timedelta(days=1)
    invite_url.save()
    url_name = 'sign_up'
    response = client.get(reverse(url_name, kwargs={"url_uuid": invite_url.uuid}))
    assert response.status_code == 403


@pytest.mark.django_db
def test_visit_sign_up_shows_correct_form(client):
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    invite_url = books_models.InviteURL.objects.create(book_club=book_club)
    url_name = 'sign_up'
    response = client.get(reverse(url_name, kwargs={"url_uuid": invite_url.uuid}))

    context = response.context[-1]
    assert 'form' in context
    form = response.context['form']
    assert isinstance(form, books_forms.InviteMemberForm)


@pytest.mark.django_db
def test_sign_up_creates_new_member(client, django_user_model):
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    invite_url = books_models.InviteURL.objects.create(book_club=book_club)
    url_name = 'sign_up'

    username = 'user'
    password = 'pwd'
    data = {
        "username": username,
        "password": password,
        "password_repeat": password
    }
    response = client.post(reverse(url_name, kwargs={"url_uuid": invite_url.uuid}), data)

    user_qs = django_user_model.objects.filter(username=username)
    assert user_qs.exists()

    user = user_qs.first()
    assert user.check_password(password)

    assert books_models.BookClubMembers.objects.filter(book_club=book_club, member=user, is_mod=False).exists()

    invite_url = books_models.InviteURL.objects.get(uuid=invite_url.uuid)
    assert invite_url.accepted

    assert response.status_code == 302
    assert response.url == reverse("index")


@pytest.mark.django_db
def test_sign_up_form_raises_error_if_username_already_exists(django_user_model):
    username = 'user'
    password = 'pwd'
    django_user_model.objects.create_user(username=username, password=password)

    data = {
        "username": username,
        "password": password,
        "password_repeat": password
    }
    form = books_forms.InviteMemberForm(data=data)
    assert not form.is_valid()


@pytest.mark.django_db
def test_sign_up_form_raises_error_if_password_repeat_incorrect(django_user_model):
    username = 'user'
    password = 'pwd'
    data = {
        "username": username,
        "password": password,
        "password_repeat": 'pwd-incorrect'
    }
    form = books_forms.InviteMemberForm(data=data)
    assert not form.is_valid()
