# Generated by Django 5.2 on 2025-06-05 11:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='books',
            field=models.ManyToManyField(blank=True, related_name='users_with_access', to='auth_app.book'),
        ),
    ]
