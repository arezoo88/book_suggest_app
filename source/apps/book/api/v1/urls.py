from django.urls import path, include
from apps.book.api.v1.views import BookViewSet, ReviewViewSet, recommended_books
from rest_framework.routers import DefaultRouter

app_name = 'book.api.v1'

router = DefaultRouter()
router.register(r'review', ReviewViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('book/', BookViewSet.as_view({'get': 'list'}), name='book'),
    path('suggest/', recommended_books, name='books_suggest')

]
