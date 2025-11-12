from books.models import Book
import pytest

@pytest.mark.django_db
def test_book():
    Book.objects.create(title="Bob", author="AlsoBob")
    assert Book.objects.count() == 1

# test urls require login

# test add_club shows correct form

# test add_club fails if club name is already in use

# test add_club fails gracefully if club slug is already in use

# test add_club form creates new club and navigates to books of new club

# test choose_club shows correct clubs

# test choose_club navigates to books of selected club

# test user can only visit club urls of club where user is member

# test books shows list of books that is part of club

# test books show reviews related to book and only of members of club

# test add_book shows correct form

# test add_book does not create duplicate entries

# test add_books creates/gets new book and new bookclub book and navigates back to books

# test review shows correct form (based on logged-in user)

# test review is correctly created