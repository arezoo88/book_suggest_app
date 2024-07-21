from django.urls import path

app_name = 'book.api.v1'
urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),


]
