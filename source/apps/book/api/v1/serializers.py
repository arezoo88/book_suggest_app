from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.book.models import Book, Review
User = get_user_model()


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

class BookRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'book', 'user', 'rating']
        read_only_fields = ['user']