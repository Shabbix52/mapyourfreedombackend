from django.urls import path
from .views import CoachingViewSet

urlpatterns = [
    path('', CoachingViewSet.as_view({'post': 'create'}), name='coaching-create'),
]