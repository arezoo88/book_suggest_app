from django.db.models import Avg
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
from rest_framework.decorators import api_view, permission_classes


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
        if instance.user != request.user:
            return Response({'error': 'You can only delete your own ratings.'}, status=status.HTTP_403_FORBIDDEN)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

# # # With orm

# def get_user_preferences(user):
#     user_ratings = Review.objects.filter(user=user)
#     genre_ratings = user_ratings.values(
#         'book__genre').annotate(avg_rating=Avg('rating'))
#     sorted_genres = sorted(
#         genre_ratings, key=lambda x: x['avg_rating'], reverse=True)
#     return [genre['book__genre'] for genre in sorted_genres]


# def recommend_books(user, num_recommendations=5):
#     preferred_genres = get_user_preferences(user)
#     rated_books = Review.objects.filter(
#         user=user).values_list('book', flat=True)
#     recommended_books = (
#         Book.objects.filter(genre__in=preferred_genres)
#         .exclude(id__in=rated_books)[:num_recommendations]
#     )
#     return recommended_books



def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def get_user_preferences(user_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT b.genre, AVG(ur.rating) as avg_rating
            FROM book_review ur
            JOIN book_book b ON ur.book_id = b.id
            WHERE ur.user_id = %s
            GROUP BY b.genre
            ORDER BY avg_rating DESC
        """, [user_id])
        return [row['genre'] for row in dictfetchall(cursor)]

def recommend_books(user_id, num_recommendations=5):
    preferred_genres = get_user_preferences(user_id)
    if not preferred_genres:
        return "There is not enough data about you."
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT b.id, b.title, b.author, b.genre
            FROM book_book b
            LEFT JOIN book_review ur ON b.id = ur.book_id
            WHERE b.genre IN %s
            AND b.id NOT IN (
                SELECT book_id 
                FROM book_review
                WHERE user_id = %s
            )
            GROUP BY b.id, b.title, b.author
            LIMIT %s
        """, [tuple(preferred_genres), user_id, num_recommendations])
        return dictfetchall(cursor)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommended_books(request):
    user_id = request.user.id
    recommended_books = recommend_books(user_id)
    serializer = BookSerializer(recommended_books, many=True)
    return Response(serializer.data)
