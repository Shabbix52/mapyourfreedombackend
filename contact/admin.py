from django.contrib import admin
from .models import ContactMessage
from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import format_html
from django import forms
from django.template.loader import render_to_string
from email.mime.image import MIMEImage
import os

class ContactMessageAdminForm(forms.ModelForm):
    reply_text = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 10, "cols": 80}),
        required=False,
        help_text="Type your reply here to send an email.",
        label="Reply"
    )

    class Meta:
        model = ContactMessage
        fields = '__all__'

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    form = ContactMessageAdminForm
    list_display = ('name', 'email', 'short_message', 'created_at', 'replied', 'reply_button')
    list_filter = ('replied', 'created_at')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('name', 'email', 'message', 'created_at', 'ip_address')
    date_hierarchy = 'created_at'
    
    def short_message(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    short_message.short_description = 'Message'
    
    def reply_button(self, obj):
        if not obj.replied:
            url = f"/admin/contact/contactmessage/{obj.id}/change/"
            return format_html(
                '<a class="button" href="{}">Reply</a>',
                url
            )
        return format_html('<span>✓ Replied</span>')
    reply_button.short_description = 'Action'
    
    def response_change(self, request, obj):
        reply_message = request.POST.get("reply_text", "").strip()
        if reply_message and not obj.replied:
            subject = f"Re: Your message to our website"
            html_content = render_to_string(
                'contact/contact_admin_reply_email.html',
                {
                    'name': obj.name,
                    'reply_message': reply_message,
                }
            )
            # Prepare the email
            from django.core.mail import EmailMultiAlternatives
            email = EmailMultiAlternatives(
                subject,
                '',  # plain text fallback
                settings.DEFAULT_FROM_EMAIL,
                [obj.email],
            )
            email.attach_alternative(html_content, "text/html")

            # Attach the banner image as inline (CID)
            banner_path = os.path.join(settings.MEDIA_ROOT, 'images', 'Map-Your_Freedom.jpeg')
            if os.path.exists(banner_path):
                with open(banner_path, 'rb') as img:
                    banner_img = MIMEImage(img.read())
                    banner_img.add_header('Content-ID', '<banner>')
                    banner_img.add_header('Content-Disposition', 'inline', filename='Map-Your_Freedom.jpeg')
                    email.attach(banner_img)

            email.send(fail_silently=False)
            obj.replied = True
            obj.save()
            self.message_user(request, "Reply sent successfully!")
        return super().response_change(request, obj)
