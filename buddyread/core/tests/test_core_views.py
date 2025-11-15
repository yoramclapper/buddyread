import pytest
from pytest_django.asserts import assertRedirects
from django.urls import reverse
import books.models as books_models
import core.forms as core_forms


# ======================================================================================================================
# TESTS REDIRECT AFTER LOGIN
# ======================================================================================================================

test_urls = ["index", "change_auth"]
@pytest.mark.parametrize("url", test_urls)
def test_anonymous_user_requires_login(client, url):
    response = client.get(reverse(url))
    assert response.status_code == 302
    assert f"/accounts/login/?next=" in response.url


def test_user_without_club_redirect_to_add_club(client, django_user_model):
    username = 'user'
    password = 'pwd'
    django_user_model.objects.create_user(username=username, password=password)

    client.login(username=username, password=password)
    response = client.get("/")

    assert response.status_code == 302
    assert response.url == reverse("add_club")

@pytest.mark.django_db
def test_user_with_single_club_redirect_to_club_page(client, django_user_model):
    username = 'user'
    password = 'pwd'
    user = django_user_model.objects.create_user(username=username, password=password)
    book_club = books_models.BookClub.objects.create(
        name="BookClub"
    )
    books_models.BookClubMembers.objects.create(
        book_club=book_club,
        member=user
    )

    client.login(username=username, password=password)
    response = client.get("/", follow=True)
    assertRedirects(
        response=response,
        expected_url=reverse("books", kwargs={"club": book_club.slug}),
        status_code=302
    )

@pytest.mark.django_db
def test_user_with_multiple_clubs_redirect_to_select_club(client, django_user_model):
    username = 'user'
    password = 'pwd'
    user = django_user_model.objects.create_user(username=username, password=password)
    for club_name in ["BookClub1", "BookClub2"]:
        book_club = books_models.BookClub.objects.create(
            name=club_name
        )
        books_models.BookClubMembers.objects.create(
            book_club=book_club,
            member=user
        )

    client.login(username=username, password=password)
    response = client.get("/", follow=True)
    assertRedirects(
        response=response,
        expected_url=reverse("choose_club"),
        status_code=302
    )


# ======================================================================================================================
# TESTS CHANGE PROFILE
# ======================================================================================================================

def test_visit_profile_is_ok(client, django_user_model):
    username = 'user'
    password = 'pwd'
    django_user_model.objects.create_user(username=username, password=password)

    client.login(username=username, password=password)
    response = client.get(reverse("change_auth"))

    assert response.status_code == 200

@pytest.mark.django_db
def test_change_username_is_ok(client, django_user_model):
    username = 'user'
    password = 'pwd'
    user = django_user_model.objects.create_user(username=username, password=password)
    new_username = "new_username"

    client.login(username=username, password=password)
    data = {
        "username": new_username,
        "current_password": password,
    }
    response = client.post(reverse("change_auth"), data)

    assert response.status_code == 302
    assert response.url == reverse("index")

    user = django_user_model.objects.get(pk=user.pk)
    assert user.username == new_username
    assert user.check_password(password)


@pytest.mark.django_db
def test_change_password_is_ok(client, django_user_model):
    username = 'user'
    password = 'pwd'
    user = django_user_model.objects.create_user(username=username, password=password)
    new_password = "new_pwd"

    client.login(username=username, password=password)
    data = {
        "username": username,
        "current_password": password,
        "new_password": new_password,
        "new_password_repeat": new_password
    }
    response = client.post(reverse("change_auth"), data)

    assert response.status_code == 302
    assert response.url == reverse("index")

    user = django_user_model.objects.get(pk=user.pk)
    assert user.username == username
    assert user.check_password(new_password)


def test_form_raises_error_if_incorrect_pwd(client, django_user_model):
    username = 'user'
    password = 'pwd'
    user = django_user_model.objects.create_user(username=username, password=password)
    new_username = "new_username"
    new_password = "new_pwd"

    data = {
        "username": new_username,
        "current_password": "incorrect_pwd",
        "new_password": new_password,
        "new_password_repeat": new_password
    }
    form = core_forms.ChangeAuthForm(data=data, user=user)

    assert not form.is_valid()
    assert form.errors['current_password'][0] == 'Huidig wachtwoord is incorrect'


def test_form_raises_error_if_new_pwd_repeat_incorrect(client, django_user_model):
    username = 'user'
    password = 'pwd'
    user = django_user_model.objects.create_user(username=username, password=password)
    new_username = "new_username"
    new_password = "new_pwd"

    data = {
        "username": new_username,
        "current_password": password,
        "new_password": new_password,
        "new_password_repeat": "incorrect_pwd_repeat"
    }
    form = core_forms.ChangeAuthForm(data=data, user=user)

    assert not form.is_valid()
    assert form.errors['__all__'][0] == 'Het nieuwe wachtwoord en de herhaling komen niet overeen'
