from django.contrib import admin
from . models import BlogPost
#             

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_author', 'category', 'status', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('title', 'content', 'writer_name')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    
    def get_author(self, obj):
        if obj.writer:
            return obj.writer.get_full_name() or obj.writer.username
        return obj.writer_name
    get_author.short_description = 'Author'