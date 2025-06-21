import stripe
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.decorators import throttle_classes
from auth_app.models import Book
from .models import Payment
from .utils import create_checkout_session

stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def checkout(request):
    book_id = request.data.get('book_id')
    print("Received book_id from frontend:", book_id)
    if not book_id:
        return Response({
            'detail': 'book_id is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        book = Book.objects.get(id=book_id)
        print("Book fetched for checkout:", book, "Language:", book.language)
    except Book.DoesNotExist:
        return Response({
            'detail': 'Book not found'
        }, status=status.HTTP_404_NOT_FOUND)

    try:
        payment = Payment.objects.create(
            user=request.user,
            book=book,
            # ...other fields...
        )
        print("Payment created:", payment)
        checkout_session = create_checkout_session(payment.id, book)

        return Response({
            "detail": checkout_session.url
        }, status=status.HTTP_200_OK)
    
    except Exception as error:
        print("Stripe error:", error)
        return Response({
            "detail": "Stripe error: " + str(error)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([])  # <--- disables throttling for this view
def stripe_webhook(request):
    print("=== Stripe webhook received! ===")
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    print("Payload:", payload)
    print("Signature header:", sig_header)
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        print("Event constructed:", event)
    except Exception as e:
        print("Webhook error:", e)
        return Response({"detail": "Invalid payload"}, status=status.HTTP_400_BAD_REQUEST)

    print("Event type:", event.get("type"))
    # Only handle checkout.session.completed
    if event["type"] == "checkout.session.completed":
        checkout_obj = event["data"]["object"]
        payment_id = checkout_obj.get('client_reference_id')
        print("Looking for Payment with id:", payment_id)
        try:
            payment = Payment.objects.get(id=payment_id)
            print("Payment found:", payment)  # Shows which payment (and book) was found
        except Payment.DoesNotExist:
            print("Payment not found for id:", payment_id)
            return Response({"detail": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)
        user = payment.user
        book = payment.book
        print("User before adding book:", user, list(user.books.all()))
        user.books.add(book)
        print("User after adding book:", user, list(user.books.all()))  # Shows the user's books after granting access
        payment.save()
        user.save()
        print("Payment and user saved successfully.")
        return Response({"detail": "OK"}, status=status.HTTP_200_OK)

    print("Event type not handled, returning 200 OK.")
    # For all other event types, just return 200 OK (do nothing)
    return Response({"detail": "Event ignored"}, status=status.HTTP_200_OK)
