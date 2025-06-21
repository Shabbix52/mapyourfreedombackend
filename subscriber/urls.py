from django.urls import path
from .views import SubscriberViewSet

urlpatterns = [
    path('', SubscriberViewSet.as_view({'post': 'create'}), name='subscriber-create'),
]