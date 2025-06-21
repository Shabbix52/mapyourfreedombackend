from django.contrib import admin
from django.http import HttpResponse
import csv
from django.utils.html import format_html
from .models import Subscriber
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import os
from django.core.mail import EmailMessage


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'subscribed_at', 'is_active', 'send_guide_button')
    list_filter = ('is_active', 'subscribed_at')
    search_fields = ('first_name', 'last_name', 'email')
    readonly_fields = ('subscribed_at', 'ip_address')
    date_hierarchy = 'subscribed_at'
    actions = ['export_subscriber', 'mark_as_active', 'mark_as_inactive', 'resend_guide']
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Name'

    def send_guide_button(self, obj):
        url = f"/admin/subscriber/subscriber/{obj.id}/resend-guide/"
        return format_html(
            '<a class="button" href="{}">Resend Guide</a>', 
            url
        )
    send_guide_button.short_description = 'Guide'
    
    def export_subscriber(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="subscriber.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['First Name', 'Last Name', 'Email', 'Subscribed At', 'Active'])
        
        for subscriber in queryset:
            writer.writerow([
                subscriber.first_name,
                subscriber.last_name,
                subscriber.email,
                subscriber.subscribed_at.strftime('%Y-%m-%d %H:%M'),
                'Yes' if subscriber.is_active else 'No'
            ])
            
        return response
    export_subscriber.short_description = "Export selected subscriber to CSV"
    
    def mark_as_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} subscriber marked as active.")
    mark_as_active.short_description = "Mark selected subscriber as active"
    
    def mark_as_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} subscriber marked as inactive.")
    mark_as_inactive.short_description = "Mark selected subscriber as inactive"
    
    def resend_guide(self, request, queryset):
        count = 0
        for subscriber in queryset:
            self.send_welcome_email(subscriber)
            count += 1
        self.message_user(request, f"Mini-guide resent to {count} subscriber.")
    resend_guide.short_description = "Resend mini-guide to selected subscriber"
    
    def send_welcome_email(self, subscriber):
        """Send welcome email with mini-guide attachment"""
        try:
            # Context for email template
            context = {
                'first_name': subscriber.first_name,
                'full_name': subscriber.full_name(),
                'email': subscriber.email,
                'site_name': getattr(settings.SITE_NAME, 'Our Website'),
                'support_email': getattr(settings.SUPPORT_EMAIL, settings.DEFAULT_FROM_EMAIL),
            }
            
            # Render email content
            html_content = render_to_string('subscriber/welcome_email.html', context)
            plain_content = strip_tags(html_content)
            
            # Create email
            subject = f"Your Mini Guide Is Ready + Let’s Talk! "
            email = EmailMessage(
                subject=subject,
                body=html_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[subscriber.email],
            )
            
            # Add HTML content
            email.content_subtype = "html"
            
            # Attach PDF
            guide_path = os.path.join(settings.MEDIA_ROOT, 'guides', 'Map-Your-Freedom-Info-Mini-Guide.pdf')
            if os.path.exists(guide_path):
                email.attach_file(guide_path)
            
            # Send email
            email.send(fail_silently=False)
            return True
            
        except Exception as e:
            print(f"Error sending welcome email: {e}")
            return False
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:subscriber_id>/resend-guide/',
                self.admin_site.admin_view(self.resend_guide_view),
                name='subscriber-resend-guide',
            ),
        ]
        return custom_urls + urls
    
    def resend_guide_view(self, request, subscriber_id):
        from django.shortcuts import redirect
        from django.contrib import messages
        
        subscriber = Subscriber.objects.get(pk=subscriber_id)
        self.send_welcome_email(subscriber)
        
        messages.success(request, f"Mini-guide resent to {subscriber.email}.")
        return redirect('admin:subscriber_subscriber_changelist')