from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.template.defaultfilters import slugify


class Book(models.Model):
    title = models.CharField(max_length=255, blank=False, null=False)
    author = models.CharField(max_length=255, blank=False, null=False)
    creation_date = models.DateField(auto_now_add=True)

    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint(fields=['title', 'author'], name='unique_title_author')
    #     ]

    def __str__(self):
        return self.title


class Review(models.Model):
    SCORES = [
        ('DNF', 'DNF'),
        ('1', '1'),
        ('1.5', '1.5'),
        ('2', '2'),
        ('2.5', '2.5'),
        ('3', '3'),
        ('3.5', '3.5'),
        ('4', '4'),
        ('4.5', '4.5'),
        ('5', '5'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    score = models.CharField(
        max_length=3,
        blank=False,
        null=False,
        choices=SCORES
    )
    comment = models.TextField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'book'], name='unique_user_book')
        ]

    def __str__(self):
        return f"{self.book.title} - {self.user.username}"


class BookClub(models.Model):
    slug = models.SlugField(primary_key=True, max_length=50, null=False, blank=False)
    name = models.CharField(unique=True, max_length=50, null=False, blank=False)
    creation_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)

    # def clean(self):
    #     super().clean()
    #     if BookClub.objects.filter(slug=slugify(self.name)).exists():
    #         raise ValidationError(f"Slug already exists for club name: {self.name}")

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"


class BookClubMembers(models.Model):
    book_club = models.ForeignKey(BookClub, on_delete=models.CASCADE, blank=False, null=False)
    member = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)
    is_mod = models.BooleanField(blank=False, null=False, default=False)

    class Meta:
        verbose_name_plural = "Book club members"


class BookClubBooks(models.Model):
    book_club = models.ForeignKey(BookClub, on_delete=models.CASCADE, blank=False, null=False)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, blank=False, null=False)
    selected_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    date_added = models.DateField(auto_now_add=True, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Book club books"
