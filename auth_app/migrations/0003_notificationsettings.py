# Generated by Django 5.2 on 2025-06-10 12:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_app', '0002_user_books'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notify_coaching', models.BooleanField(default=True, help_text='Notify admin for new Coaching submissions')),
                ('notify_subscriber', models.BooleanField(default=True, help_text='Notify admin for new Subscribers')),
                ('notify_contact', models.BooleanField(default=True, help_text='Notify admin for new Contact messages')),
            ],
            options={
                'verbose_name': 'Notification Settings',
                'verbose_name_plural': 'Notification Settings',
            },
        ),
    ]
