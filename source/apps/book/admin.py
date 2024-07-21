from django.contrib import admin
from apps.book.models import Book, Review


class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'genre', 'author')
    list_filter = ('genre',)


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'rating')
    list_filter = ('rating',)


admin.site.register(Book, BookAdmin)
admin.site.register(Review, ReviewAdmin)
