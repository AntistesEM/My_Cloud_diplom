# Generated by Django 5.1.7 on 2025-03-25 11:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api_app', '0003_user_groups_user_is_active_user_is_staff_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='password_hash',
        ),
    ]
