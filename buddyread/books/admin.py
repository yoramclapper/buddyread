from django.contrib import admin
from .models import Book, Review, BookClub, BookClubMembers, BookClubBooks

admin.site.register(Book)
admin.site.register(Review)

class BookClubMembersInline(admin.TabularInline):
    model = BookClubMembers
    extra = 1

@admin.register(BookClub)
class BookClubAdmin(admin.ModelAdmin):
    list_display = ('naam', 'creation_date')
    inlines = [BookClubMembersInline]

