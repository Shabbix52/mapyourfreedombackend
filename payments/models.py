from django.db import models
from django.contrib.auth import get_user_model
from auth_app.models import Book

# Create your models here.

User = get_user_model()

class Payment(models.Model): 
    user = models.ForeignKey(User, models.CASCADE)
    book = models.ForeignKey(Book, models.CASCADE, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    total_amount = models.FloatField(null=True, blank=True)
    currency = models.CharField(max_length=256, null=True, blank=True)
    session_id = models.CharField(max_length=512, null=True, blank=True)
    payment_intent_id = models.CharField(max_length=512, null=True, blank=True)
    status = models.CharField(max_length=256, null=True, blank=True)
    payment_status = models.CharField(max_length=256, null=True, blank=True)
    customer_email = models.EmailField(null=True, blank=True)
    session_created_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.customer_email if self.customer_email else self.user.email}" + (f":{self.book.language}" if self.book else '')

