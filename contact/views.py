from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import UserRateThrottle
from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from email.mime.image import MIMEImage
import os
from django.conf import settings
from .models import ContactMessage
from .serializers import ContactMessageSerializer
from auth_app.models import NotificationSettings  # or from core.models if that's where it is

class ContactThrottle(UserRateThrottle):
    scope = 'contact_submit'

class ContactViewSet(CreateModelMixin, GenericViewSet):
    """
    API endpoint for submitting contact messages
    """
    queryset = ContactMessage.objects.none()
    serializer_class = ContactMessageSerializer
    permission_classes = [AllowAny]
    throttle_classes = [ContactThrottle]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get IP address
        ip = self.get_client_ip(request)

        # Save message with IP
        contact_message = serializer.save(ip_address=ip)

        # Check notification setting before sending admin email
        notify_setting = NotificationSettings.objects.first()
        if not notify_setting or notify_setting.notify_contact:
            self.send_notification_email(contact_message)
        self.send_user_thank_you_email(contact_message)

        return Response(
            {"message": "Your message has been received. We'll get back to you soon."},
            status=status.HTTP_201_CREATED
        )

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def send_notification_email(self, message):
        subject = f"New Contact Form Submission from {message.name}"
        email_body = f"""
You have received a new message from the contact form:

Name: {message.name}
Email: {message.email}

Message:
{message.message}

Time: {message.created_at}


You can manage this message in the admin panel.
        """

        try:
            EmailMessage(
                subject=subject,
                body=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[settings.ADMIN_EMAIL],
            ).send(fail_silently=False)
        except Exception as e:
            print(f"Error sending notification email: {e}")

    def send_user_thank_you_email(self, message):
        subject = "Thanks for Reaching Out – We’ll Be in Touch Soon!"
        context = {
            "name": message.name,
        }
        html_content = render_to_string('contact/contact_thank_you_email.html', context)
        text_content = f"""
Hi {message.name},

Thank you for contacting us! 🙌
We’ve received your message and appreciate you taking the time to reach out.

Someone from our team will get back to you within the next 24–48 hours. In the meantime, feel free to explore our website.

Looking forward to speaking with you soon!

Warm regards,  
Fatemi Ghani  
Author, Coach & Crown Ambassador  
https://mapyourfreedom.com
        """

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[message.email],
        )
        email.attach_alternative(html_content, "text/html")

        # Attach banner image as inline (CID)
        banner_path = os.path.join(settings.MEDIA_ROOT, 'images', 'Map-Your_Freedom.jpeg')
        if os.path.exists(banner_path):
            with open(banner_path, 'rb') as img:
                banner_img = MIMEImage(img.read())
                banner_img.add_header('Content-ID', '<banner>')
                banner_img.add_header('Content-Disposition', 'inline', filename='Map-Your_Freedom.jpeg')
                email.attach(banner_img)

        email.send(fail_silently=False)
