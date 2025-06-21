from django.urls import path
from .views import checkout, stripe_webhook

urlpatterns = [
    path('checkout/', checkout),
    path('stripe_webhook/', stripe_webhook)
]