from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import Book, User, NotificationSettings

# Register your models here. 
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "phone", "gender")}),
        (_("Permissions"), {"fields": ("is_staff", "groups")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
        (_("Book Access"), {"fields": ("books",)}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "phone", "first_name", "last_name", "password1", "password2"),
            },
        ),
    )

    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    filter_horizontal = ('books',)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'language')

@admin.register(NotificationSettings)
class NotificationSettingsAdmin(admin.ModelAdmin):
    list_display = (
        'coaching_notification',
        'guide_notification',
        'contact_notification',
    )

    def coaching_notification(self, obj):
        return obj.notify_coaching
    coaching_notification.boolean = True
    coaching_notification.short_description = "Coaching Notification"

    def guide_notification(self, obj):
        return obj.notify_subscriber
    guide_notification.boolean = True
    guide_notification.short_description = "Guide Notification"

    def contact_notification(self, obj):
        return obj.notify_contact
    contact_notification.boolean = True
    contact_notification.short_description = "Contact Notification"