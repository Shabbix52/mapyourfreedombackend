from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import UserRateThrottle
from django.conf import settings
from .models import Subscriber
from .serializers import SubscriberSerializer
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from email.mime.image import MIMEImage
import os
import threading
import logging
import base64
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from auth_app.models import NotificationSettings

# Set up logging
logger = logging.getLogger(__name__)

class SubscriberThrottle(UserRateThrottle):
    scope = 'subscriber_submit'

class SubscriberViewSet(CreateModelMixin, GenericViewSet):
    """
    API endpoint for newsletter subscribers
    """
    queryset = Subscriber.objects.none()
    serializer_class = SubscriberSerializer
    permission_classes = [AllowAny]
    throttle_classes = [SubscriberThrottle]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get IP address
        ip = self.get_client_ip(request)
        
        # Check if the email exists but is marked as inactive
        email = serializer.validated_data['email']
        notify_admin = serializer.validated_data.get('notify_admin', False)
        
        try:
            existing_subscriber = Subscriber.objects.get(email=email, is_active=False)
            # Reactivate the subscriber
            existing_subscriber.first_name = serializer.validated_data['first_name']
            existing_subscriber.last_name = serializer.validated_data['last_name']
            existing_subscriber.notify_admin = notify_admin
            existing_subscriber.is_active = True
            existing_subscriber.ip_address = ip
            existing_subscriber.save()
            subscriber = existing_subscriber
        except Subscriber.DoesNotExist:
            # Create new subscriber
            subscriber = serializer.save(ip_address=ip, notify_admin=notify_admin)
        
        # Send emails in background thread to prevent blocking the response
        email_thread = threading.Thread(
            target=self.send_emails,
            args=[subscriber.id]
        )
        email_thread.start()
        
        return Response({
            "message": "Thank you for subscribing! Check your email for your free mini-guide."
        }, status=status.HTTP_201_CREATED)
    
    def send_emails(self, subscriber_id):
        """Send welcome email and conditionally send admin notification"""
        subscriber = Subscriber.objects.get(pk=subscriber_id)

        # Always send welcome email with mini-guide
        self.send_welcome_email(subscriber)

        # Only send admin notification if enabled in NotificationSettings
        notify_setting = NotificationSettings.objects.first()
        if not notify_setting or notify_setting.notify_subscriber:
            self.send_admin_notification(subscriber)
            logger.info(f"Admin notification sent for subscriber: {subscriber.email}")
        else:
            logger.info(f"Admin notification skipped for subscriber: {subscriber.email} (notification disabled in settings)")
    
    def get_logo_base64(self):
        """Convert logo image to base64 for embedding"""
        try:
            # Try different possible paths for the logo
            logo_paths = [
                os.path.join(settings.MEDIA_ROOT, 'images', 'Map-Your_Freedom.jpeg'),
                os.path.join(settings.BASE_DIR, 'media', 'images', 'Map-Your_Freedom.jpeg'),
                os.path.join(settings.STATIC_ROOT, 'images', 'Map-Your_Freedom.jpeg'),
                os.path.join(settings.BASE_DIR, 'static', 'images', 'Map-Your_Freedom.jpeg'),
            ]
            
            for logo_path in logo_paths:
                if os.path.exists(logo_path):
                    with open(logo_path, 'rb') as image_file:
                        image_data = image_file.read()
                        base64_image = base64.b64encode(image_data).decode('utf-8')
                        
                        # Determine image type
                        if logo_path.lower().endswith('.jpeg') or logo_path.lower().endswith('.jpg'):
                            mime_type = 'image/jpeg'
                        elif logo_path.lower().endswith('.png'):
                            mime_type = 'image/png'
                        else:
                            mime_type = 'image/jpeg'  # default
                        
                        logger.info(f"Logo found and converted to base64: {logo_path}")
                        return f"data:{mime_type};base64,{base64_image}"
            
            logger.warning("Logo not found in any of the expected paths")
            return None
            
        except Exception as e:
            logger.error(f"Error converting logo to base64: {e}")
            return None
    
    def send_welcome_email(self, subscriber):
        """Send welcome email with mini-guide attachment and embedded logo"""
        try:
            # Get the logo as base64
            logo_base64 = self.get_logo_base64()
            
            # Context for email template
            context = {
                'first_name': subscriber.first_name,
                'full_name': subscriber.full_name(),
                'email': subscriber.email,
                'site_name': getattr(settings, 'SITE_NAME', 'Our Website'),
                'support_email': getattr(settings, 'SUPPORT_EMAIL', settings.DEFAULT_FROM_EMAIL),
                'logo_base64': logo_base64,  # Use base64 instead of URL
            }
            
            # Render email content
            html_content = render_to_string('subscriber/welcome_email.html', context)
            plain_content = strip_tags(html_content)
            
            # Create email using EmailMultiAlternatives for better HTML support
            subject = f"Your Mini Guide Is Ready + Let's Talk!"
            
            # Use EmailMultiAlternatives for better HTML email support
            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_content,  # Plain text version
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[subscriber.email],
            )
            
            # Attach HTML content
            email.attach_alternative(html_content, "text/html")
            
            # If we have logo data, attach it as an embedded image
            if logo_base64:
                try:
                    # Extract base64 data (remove data:image/jpeg;base64, part)
                    if 'base64,' in logo_base64:
                        image_data = base64.b64decode(logo_base64.split('base64,')[1])
                        
                        # Create MIMEImage
                        image = MIMEImage(image_data)
                        image.add_header('Content-ID', '<logo>')
                        image.add_header('Content-Disposition', 'inline', filename='logo.jpg')
                        
                        # Attach the image
                        email.attach(image)
                        logger.info("Logo attached as embedded image")
                except Exception as img_error:
                    logger.error(f"Error attaching embedded logo: {img_error}")
            
            # Attach PDF with better error handling
            guide_path = os.path.join(settings.MEDIA_ROOT, 'guides', 'Map-Your-Freedom-Info-Mini-Guide.pdf')
            logger.info(f"Looking for PDF at: {guide_path}")
            
            if os.path.exists(guide_path):
                try:
                    logger.info(f"PDF found, attaching to email")
                    email.attach_file(guide_path)
                except Exception as attach_error:
                    logger.error(f"Error attaching PDF file: {attach_error}")
            else:
                logger.error(f"PDF file not found at path: {guide_path}")
                
                # Try alternate locations
                alternate_paths = [
                    os.path.join(settings.MEDIA_ROOT, 'guides', 'Map-Your-Freedom-Info-Mini-Guide.pdf'),
                    os.path.join(settings.BASE_DIR, 'media', 'guides', 'Map-Your-Freedom-Info-Mini-Guide.pdf'),
                    os.path.join(settings.BASE_DIR, 'static', 'guides', 'Map-Your-Freedom-Info-Mini-Guide.pdf'),
                    r'E:\freelance-projects\Your-Freedom-Backend\core\media\guides\Map-Your-Freedom-Info-Mini-Guide.pdf',
                ]
                
                for alt_path in alternate_paths:
                    logger.info(f"Trying alternate path: {alt_path}")
                    if os.path.exists(alt_path):
                        try:
                            logger.info(f"PDF found at alternate path, attaching to email")
                            email.attach_file(alt_path)
                            break
                        except Exception as alt_attach_error:
                            logger.error(f"Error attaching PDF from alternate path: {alt_attach_error}")
            
            # Attach the banner image as an embedded image with CID 'banner'
            try:
                banner_path = os.path.join(settings.MEDIA_ROOT, 'images', 'Map-Your_Freedom.jpeg')
                if os.path.exists(banner_path):
                    with open(banner_path, 'rb') as banner_file:
                        banner_data = banner_file.read()
                        banner_image = MIMEImage(banner_data)
                        banner_image.add_header('Content-ID', '<banner>')
                        banner_image.add_header('Content-Disposition', 'inline', filename='Map-Your_Freedom.jpeg')
                        email.attach(banner_image)
                        logger.info("Banner image attached as embedded image")
                else:
                    logger.warning(f"Banner image not found at: {banner_path}")
            except Exception as banner_error:
                logger.error(f"Error attaching banner image: {banner_error}")
            
            # Send email
            email.send(fail_silently=False)
            logger.info(f"Email sent successfully to {subscriber.email}")
            
        except Exception as e:
            logger.error(f"Error sending welcome email: {e}")
    
    def send_admin_notification(self, subscriber):
        """Send notification to admin about new subscriber"""
        try:
            subject = f"New Newsletter Subscriber: {subscriber.full_name()}"
            message = f"""
            You have a new newsletter subscriber:
            
            Name: {subscriber.full_name()}
            Email: {subscriber.email}
            Subscribed at: {subscriber.subscribed_at}
            Admin Notification: {'Requested' if subscriber.notify_admin else 'Not Requested'}
            
            You can manage subscribers in the admin panel.
            """
            
            admin_email = getattr(settings, 'ADMIN_EMAIL', settings.DEFAULT_FROM_EMAIL)
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[admin_email],
            )
            
            email.send(fail_silently=False)
            logger.info(f"Admin notification sent to {admin_email}")
            
        except Exception as e:
            logger.error(f"Error sending admin notification: {e}")
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([])  # <--- disables throttling for this view
def subscribe(request):
    ...
