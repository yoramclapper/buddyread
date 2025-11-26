import pytest
from pytest_django.asserts import assertRedirects
from django.template.defaultfilters import slugify
from django.urls import reverse
import books.models as books_models
import books.forms as books_forms


# ======================================================================================================================
# TESTS REDIRECT AFTER LOGIN
# ======================================================================================================================


test_urls = ["add_club", "choose_club"]
@pytest.mark.parametrize("url", test_urls)
def test_anonymous_user_requires_login_url_without_club(client, url):
    response = client.get(reverse(url))
    assert response.status_code == 302
    assert f"/accounts/login/?next=" in response.url


test_urls = ["books", "add_book"]
@pytest.mark.parametrize("url", test_urls)
def test_anonymous_user_requires_login_url_with_club(client, url):
    response = client.get(reverse(url, kwargs={"club": "club_slug"}))
    assert response.status_code == 302
    assert f"/accounts/login/?next=" in response.url


def test_anonymous_user_requires_login_for_book_review(client):
    response = client.get(reverse("review", kwargs={"club": "club_slug", "book_pk": 1}))
    assert response.status_code == 302
    assert f"/accounts/login/?next=" in response.url


# ======================================================================================================================
# TESTS CREATE BOOK CLUB
# ======================================================================================================================

@pytest.mark.django_db
def test_model_book_club_creates_slug_on_save():
    book_club_name = "Bookclub"

    book_club = books_models.BookClub(name=book_club_name)
    assert book_club.slug == ''

    book_club.save()
    assert book_club.slug == slugify(book_club_name)

@pytest.mark.django_db
def test_add_club_is_ok(client, django_user_model):
    username = 'user'
    password = 'pwd'
    user = django_user_model.objects.create_user(username=username, password=password)
    book_club_name = "Bookclub"

    client.login(username=username, password=password)
    response = client.post(reverse("add_club"), data={"name": book_club_name}, follow=True)

    try:
        book_club = books_models.BookClub.objects.get(slug=slugify(book_club_name))
    except Exception as exc:
        pytest.fail(f"Could not find book club {book_club_name}: {exc}")

    try:
        member = books_models.BookClubMembers.objects.get(book_club=book_club, member=user)
    except Exception as exc:
        pytest.fail(f"Could not find member '{user.username}' at book club {book_club_name}: {exc}")

    assert member.is_mod

    assertRedirects(
        response=response,
        expected_url=reverse("books", kwargs={"club": book_club.slug}),
        status_code=302
    )


@pytest.mark.django_db
def test_form_book_club_raises_error_if_club_name_already_exists():
    book_club_name = "Bookclub"
    books_models.BookClub.objects.create(name=book_club_name)

    data = {
        "name": book_club_name
    }
    form = books_forms.BookClubForm(data=data)

    assert not form.is_valid()


# @pytest.mark.django_db
# def test_form_book_club_raises_error_if_slug_already_exists():
#     books_models.BookClub.objects.create(name="Bookclub")
#
#     data = {
#         "name": "Bookclub!"
#     }
#     form = books_forms.BookClubForm(data=data)
#
#     assert not form.is_valid()


@pytest.mark.django_db
def test_choose_club_shows_only_clubs_of_user(client, django_user_model):

    username = 'user'
    password = 'pwd'
    user = django_user_model.objects.create_user(username=username, password=password)
    book_club_1 = books_models.BookClub.objects.create(name="Bookclub 1")
    book_club_2 = books_models.BookClub.objects.create(name="Bookclub 2")
    books_models.BookClubMembers.objects.create(book_club=book_club_1, member=user)
    books_models.BookClubMembers.objects.create(book_club=book_club_2, member=user)

    # setup other book club
    user_2 = django_user_model.objects.create_user(username="user3", password=password)
    book_club_3 = books_models.BookClub.objects.create(name="Bookclub 3")
    books_models.BookClubMembers.objects.create(book_club=book_club_3, member=user_2)

    client.login(username=username, password=password)
    response = client.get(reverse("choose_club"))

    context = response.context[-1]
    assert 'book_clubs' in context

    book_clubs = context["book_clubs"]
    assert len(book_clubs) == 2
    assert book_club_1 in book_clubs
    assert book_club_2 in book_clubs


# ======================================================================================================================
# TESTS BOOK CLUB MEMBERSHIP
# ======================================================================================================================


test_urls = ["books", "add_book"]
@pytest.mark.parametrize("url", test_urls)
@pytest.mark.django_db
def test_user_not_allowed_to_clubs_without_membership(client, django_user_model, url):
    username = 'user'
    password = 'pwd'
    user = django_user_model.objects.create_user(username=username, password=password)
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    books_models.BookClubMembers.objects.create(book_club=book_club, member=user)

    user_2 = django_user_model.objects.create_user(username="user2", password=password)
    book_club_2 = books_models.BookClub.objects.create(name="Bookclub2")
    books_models.BookClubMembers.objects.create(book_club=book_club_2, member=user_2)

    client.login(username=username, password=password)
    response = client.get(reverse(url, kwargs={"club": book_club_2.slug}))
    assert response.status_code == 403


@pytest.mark.django_db
def test_user_not_allowed_to_review_without_membership(client, django_user_model):
    username = 'user'
    password = 'pwd'
    user = django_user_model.objects.create_user(username=username, password=password)
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    books_models.BookClubMembers.objects.create(book_club=book_club, member=user)

    user_2 = django_user_model.objects.create_user(username="user2", password=password)
    book_club_2 = books_models.BookClub.objects.create(name="Bookclub2")
    books_models.BookClubMembers.objects.create(book_club=book_club_2, member=user_2)
    book = books_models.Book.objects.create(title="Title", author="Author")
    books_models.BookClubBooks.objects.create(book_club=book_club_2, book=book)

    client.login(username=username, password=password)
    response = client.get(reverse("review", kwargs={"club": book_club_2.slug, "book_pk": book.pk}))
    assert response.status_code == 403


# ======================================================================================================================
# TESTS BOOK CLUB RELATED BOOKS AND REVIEWS
# ======================================================================================================================


@pytest.mark.django_db
def test_books_main_page_is_ok(client, django_user_model):

    # setup books
    book = books_models.Book.objects.create(title="Title 1", author="Author 1")
    book_2 = books_models.Book.objects.create(title="Title 2", author="Author 2")

    # setup main book club
    username = 'user'
    password = 'pwd'
    user = django_user_model.objects.create_user(username=username, password=password)
    user_2 = django_user_model.objects.create_user(username="user2", password=password)
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    books_models.BookClubMembers.objects.create(book_club=book_club, member=user)
    books_models.BookClubMembers.objects.create(book_club=book_club, member=user_2)
    book_club_book_1 = books_models.BookClubBooks.objects.create(book_club=book_club, book=book)
    book_club_book_2 = books_models.BookClubBooks.objects.create(book_club=book_club, book=book_2)
    review_1 = books_models.Review.objects.create(user=user, book=book, score='1')
    review_2 = books_models.Review.objects.create(user=user_2, book=book, score='2')

    # setup other book club
    user_3 = django_user_model.objects.create_user(username="user3", password=password)
    book_club_2 = books_models.BookClub.objects.create(name="Bookclub 2")
    books_models.BookClubMembers.objects.create(book_club=book_club_2, member=user_3)
    books_models.BookClubBooks.objects.create(book_club=book_club_2, book=book)
    books_models.Review.objects.create(user=user_3, book=book, score='3')

    client.login(username=username, password=password)
    response = client.get(reverse("books", kwargs={"club": book_club.slug}))

    context = response.context[-1]
    assert all(keyword in context for keyword in ["books", "club", "book_clubs"])

    books, club, book_clubs = context["books"], context["club"], context["book_clubs"]
    assert club == book_club
    assert len(book_clubs) == 0  # user is member of exactly one club: book club is not displayed

    # assert that only books of book club are displayed
    assert books.count() == 2
    assert book_club_book_1 in books
    assert book_club_book_2 in books

    # assert that only reviews of book club are displayed
    all_reviews = books_models.Review.objects.filter(book=book)
    club_reviews = books.filter(book=book).first().book.review_set.all()
    assert all_reviews.count() == 3
    assert club_reviews.count() == 2
    assert review_1 in club_reviews
    assert review_2 in club_reviews


@pytest.mark.django_db
def test_add_book_is_ok(client, django_user_model):
    username = 'user'
    password = 'pwd'
    user = django_user_model.objects.create_user(username=username, password=password)
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    books_models.BookClubMembers.objects.create(book_club=book_club, member=user)
    book_title = "Title"
    book_author = "Author"

    client.login(username=username, password=password)
    response = client.post(
        reverse("add_book", kwargs={"club": book_club.slug}),
        data={"title": book_title, "author": book_author},
        follow=True
    )

    try:
        book = books_models.Book.objects.get(title=book_title, author=book_author)
    except Exception as exc:
        pytest.fail(f"Could not find book {book_title}, {book_author}: {exc}")

    try:
        books_models.BookClubBooks.objects.get(book_club=book_club, book=book)
    except Exception as exc:
        pytest.fail(f"Could not find book '{book}' at book club {book_club.name}: {exc}")

    assertRedirects(
        response=response,
        expected_url=reverse("books", kwargs={"club": book_club.slug}),
        status_code=302
    )


@pytest.mark.django_db
def test_add_review_is_ok(client, django_user_model):
    username = 'user'
    password = 'pwd'
    user = django_user_model.objects.create_user(username=username, password=password)
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    books_models.BookClubMembers.objects.create(book_club=book_club, member=user)
    book = books_models.Book.objects.create(title="Title", author="Author")

    client.login(username=username, password=password)
    response = client.post(
        reverse("review", kwargs={"club": book_club.slug, "book_pk": book.pk}),
        data={"score": '1', "comment": "Comment"},
        follow=True
    )

    try:
        books_models.Review.objects.get(user=user, book=book)
    except Exception as exc:
        pytest.fail(f"Could not find review for book {book.name} of user {user.username}: {exc}")

    assertRedirects(
        response=response,
        expected_url=reverse("books", kwargs={"club": book_club.slug}),
        status_code=302
    )


# ======================================================================================================================
# TESTS MODERATE BOOK CLUBS
# ======================================================================================================================


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
def test_visit_delete_club_member_of_self_as_mod_redirects(client, django_user_model):
    username = 'user'
    password = 'pwd'
    user = django_user_model.objects.create_user(username=username, password=password)
    book_club = books_models.BookClub.objects.create(name="Bookclub")
    member = books_models.BookClubMembers.objects.create(book_club=book_club, member=user, is_mod=True)
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
