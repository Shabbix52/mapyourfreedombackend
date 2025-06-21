from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet
from .models import CoachingInfo
from .serializers import CoachingInfoSerializer
from django.core.mail import EmailMessage
from django.conf import settings


class CoachingViewSet(GenericViewSet):
    """
    API endpoint for submitting coaching messages
    """
    queryset = CoachingInfo.objects.none()
    serializer_class = CoachingInfoSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Save message
        coaching_message = serializer.save()

        # Send emails
        self.send_notification_email(coaching_message)
        self.send_user_thank_you_email(coaching_message)

        return Response(
            {"message": "Your message has been received. We'll get back to you soon."},
            status=status.HTTP_201_CREATED
        )

    def send_notification_email(self, message):
        subject = f"New Coaching Form Submission from {message.name}"
        email_body = f"""
You have received a new message from the coaching form:

Name: {message.name}
Email: {message.email}

Message:
{message.message}

Company Name: {message.compyany_name}
        """
        try:
            EmailMessage(
                subject=subject,
                body=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[settings.ADMIN_EMAIL],
            ).send(fail_silently=False)
        except Exception as e:
            print(f"Failed to send admin email: {e}")

    def send_user_thank_you_email(self, message):
        subject = "You're One Step Closer – Thanks for Your Introduction!"
        email_body = f"""
Hi {message.name},

Thank you for taking the time to share your details and formally introduce yourself — I truly appreciate it!

Your interest in my 8-week Personal Coaching Program means a lot. Based on what you’ve shared, I’ll take some time to review your responses and understand how I can best support your journey.

You’ll hear back from me shortly to discuss the next steps and explore how we can work together.

Looking forward to connecting with you soon!

Warm regards,  
Fatemi Ghani  
Author, Coach & Crown Ambassador  
https://mapyourfreedom.com
        """
        try:
            EmailMessage(
                subject=subject,
                body=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[message.email],
            ).send(fail_silently=False)
        except Exception as e:
            print(f"Failed to send thank-you email: {e}")
