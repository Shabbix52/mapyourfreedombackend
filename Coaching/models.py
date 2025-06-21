from django.db import models

class CoachingInfo(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    compyany_name = models.CharField(max_length=100, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    replied = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Coaching Info'
        verbose_name_plural = 'Coaching Info'

    def __str__(self):
        return f"{self.name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
