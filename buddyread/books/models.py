from django.db import models
from django.contrib.auth.models import User


class Book(models.Model):
    title = models.CharField(max_length=255, blank=False, null=False)
    author = models.CharField(max_length=255, blank=False, null=False)
    creation_date = models.DateField(auto_now_add=True)


class Review(models.Model):
    SCORES = [
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
    comment = models.CharField(max_length=255, blank=True, null=True)
