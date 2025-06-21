from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import BlogPost
from .serializers import BlogPostSerializer
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.throttling import AnonRateThrottle

class IsAdminOrReadOnly(BasePermission):
    """
    Allow read-only access for unauthenticated users,
    but only admin users can write.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class BlogPostViewSet(viewsets.ModelViewSet):
    """
    API endpoint for blog posts
    """
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status']
    search_fields = ['title', 'content', 'writer_name']
    ordering_fields = ['created_at', 'updated_at', 'title']
    throttle_classes = []  # disables throttling for this viewset
    
    def get_queryset(self):
        # By default, only show published posts to anonymous users
        queryset = BlogPost.objects.all()
        
        # If not authenticated or not admin, filter to only published posts
        if not self.request.user.is_authenticated or not self.request.user.is_staff:
            queryset = queryset.filter(status='published')
            
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        # Set writer to current user if not explicitly specified
        if not serializer.validated_data.get('writer'):
            serializer.save(writer=self.request.user)
        else:
            serializer.save()