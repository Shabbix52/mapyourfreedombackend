from django.urls import path
from .views import ContactViewSet

urlpatterns = [
    path('', ContactViewSet.as_view({'post': 'create'}), name='contact-create'),
]