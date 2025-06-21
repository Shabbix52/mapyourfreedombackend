from django.contrib import admin

from .models import CoachingInfo

class CoachingAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'compyany_name', 'created_at', 'replied')
    list_filter = ('replied',)
    search_fields = ('name', 'email', 'compyany_name')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    list_per_page = 20
    readonly_fields = ('created_at', 'replied')
    fieldsets = (
        (None, {
            'fields': ('name', 'email', 'compyany_name', 'message', 'created_at', 'replied')
        }),
    )
    actions = ['mark_as_replied']
    def mark_as_replied(self, request, queryset):
        queryset.update(replied=True)
        self.message_user(request, "Selected messages marked as replied.")
    mark_as_replied.short_description = "Mark selected messages as replied"
admin.site.register(CoachingInfo, CoachingAdmin)
from django.utils.html import format_html
