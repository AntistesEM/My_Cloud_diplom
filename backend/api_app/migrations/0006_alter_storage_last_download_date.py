# Generated by Django 5.1.7 on 2025-03-29 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_app', '0005_storage_token_storage_token_expiration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='storage',
            name='last_download_date',
            field=models.DateTimeField(blank=True, db_column='lastdownloaddate', null=True),
        ),
    ]
