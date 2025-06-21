from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet, CustomUserViewSet

router = DefaultRouter()
router.register('books', BookViewSet)

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('reset_password_confirm/<str:uid>/<str:token>/', CustomUserViewSet.as_view({'post': 'reset_password_confirm'}), name='reset_password_confirm'),
] + router.urls
