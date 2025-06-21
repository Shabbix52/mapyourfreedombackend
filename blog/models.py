from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model

User = get_user_model()

class Category(models.TextChoices):
    BUSINESS = 'business', 'Business'
    WELLNESS = 'wellness', 'Wellness and Health'
    TRAVEL = 'travel', 'Travel'
    PERSONAL = 'personal', 'Personal Development'

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    writer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='blog_posts',
        null=True,
        blank=True,
    )
    writer_name = models.CharField(
        max_length=100, 
        blank=True, 
        help_text="Writer's name if not linked to a user"
    )
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.BUSINESS
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    status = models.CharField(
        max_length=10,
        choices=[('draft', 'Draft'), ('published', 'Published')],
        default='draft'
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['slug']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Generate slug if not provided
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            
            # Ensure slug is unique
            while BlogPost.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
                
            self.slug = slug
        
        # Set writer_name if writer is provided but writer_name is not
        if self.writer and not self.writer_name:
            self.writer_name = self.writer.get_full_name() or self.writer.username
            
        super().save(*args, **kwargs)