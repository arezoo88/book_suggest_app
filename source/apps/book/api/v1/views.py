from rest_framework.viewsets import ModelViewSet
from apps.book.api.v1.serializers import BookSerializer, BookRatingSerializer
from apps.book.models import Book, Review
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404


User = get_user_model()


class BookViewSet(ModelViewSet):
    # queryset = Book.objects.all() ##when use orm not raw query
    permission_classes = (IsAuthenticated,)
    serializer_class = BookSerializer
    # filter_backends = (DjangoFilterBackend,)
    # filterset_fields = ('genre')

    def get_queryset(self):
        genre = self.request.query_params.get('genre')

        query = "SELECT * FROM book_book"
        params = []

        if genre:
            query += " WHERE genre = %s"
            params.append(genre)

        with connection.cursor() as cursor:
            cursor.execute(query, params)
            columns = [col[0] for col in cursor.description]
            return [
                Book(
                    id=row[columns.index('id')],
                    title=row[columns.index('title')],
                    author=row[columns.index('author')],
                    genre=row[columns.index('genre')],
                    created_at=row[columns.index('created_at')],
                    updated_at=row[columns.index('updated_at')]
                )
                for row in cursor.fetchall()
            ]


class ReviewViewSet(ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = BookRatingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        book_id = request.data.get('book')
        rating = request.data.get('rating')

        if not book_id or not rating:
            return Response({'error': 'Both book and rating are required.'}, status=status.HTTP_400_BAD_REQUEST)

        book = get_object_or_404(Book, id=book_id)

        review_instance, created = Review.objects.update_or_create(
            book=book,
            user=request.user,
            defaults={'rating': rating}
        )

        serializer = self.get_serializer(review_instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        if instance.user != request.user:
            return Response({'error': 'You can only update your own ratings.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        print(11,instance)

        if instance.user != request.user:
            return Response({'error': 'You can only delete your own ratings.'}, status=status.HTTP_403_FORBIDDEN)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
