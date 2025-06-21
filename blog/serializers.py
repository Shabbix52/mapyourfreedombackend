from rest_framework import serializers
from .models import BlogPost

class BlogPostSerializer(serializers.ModelSerializer):
    writer_name = serializers.SerializerMethodField()
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'writer', 'writer_name', 'category', 
            'category_display', 'content', 'created_at', 'updated_at', 
            'slug', 'image', 'status'
        ]
        read_only_fields = ['created_at', 'updated_at', 'slug']
    
    def get_writer_name(self, obj):
        if obj.writer:
            return obj.writer.get_full_name() or obj.writer.username
        return obj.writer_name
    

    