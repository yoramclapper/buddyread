from django.db import models


# class Author(models.Model):
#     name = models.CharField(max_length=255, blank=False, null=False)
#
#
# class Book(models.Model):
#     title = models.CharField(max_length=255, blank=False, null=False)
#     author = models.ForeignKey(Author, on_delete=models.CASCADE)
#     pages = models.PositiveIntegerField(blank=True, null=True)
#
#
# class Status(models.Model):
#     STATUS_CHOICES = (
#         ('P', 'In progress'),
#         ('F', 'Finished'),
#         ('D', 'DNF'),
#         ('W', 'Wishlist'),
#     )
#
#     book = models.ForeignKey(Book, on_delete=models.CASCADE)
#     start_date = models.DateField(blank=False, null=False)
#     current_status = models.CharField(max_length=1, choices=STATUS_CHOICES)
#
#
# class Review(models.Model):
#     # user (https://www.geeksforgeeks.org/python/how-to-use-user-model-in-django/)
#     book = models.ForeignKey(Book, on_delete=models.CASCADE)
#     score = models.PositiveIntegerField(blank=False, null=False)
#     comment = models.TextField()