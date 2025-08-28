from django.db import models
from django.contrib.auth.models import User


class Book(models.Model):
    title = models.CharField(max_length=255, blank=False, null=False)
    author = models.CharField(max_length=255, blank=False, null=False)
    creation_date = models.DateField(auto_now_add=True)

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

    def __str__(self):
        return f"{self.book.title} - {self.user.username}"
