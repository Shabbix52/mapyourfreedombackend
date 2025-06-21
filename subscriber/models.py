from django.db import models

class Subscriber(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    notify_admin = models.BooleanField(
        default=False, 
        help_text="Send notification to admin when user subscribes"
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-subscribed_at']
        verbose_name = 'Guide Sub'
        verbose_name_plural = 'List of Subscribers'
        
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    def full_name(self):
        return f"{self.first_name} {self.last_name}"