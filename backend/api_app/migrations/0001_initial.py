# Generated by Django 5.1.7 on 2025-03-17 19:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id_user', models.AutoField(primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=128, unique=True)),
                ('username', models.CharField(max_length=128, unique=True)),
                ('fullname', models.CharField(max_length=128)),
                ('role', models.CharField(default='user', max_length=128)),
                ('password_hash', models.CharField(max_length=128)),
            ],
            options={
                'db_table': 'users',
            },
        ),
        migrations.CreateModel(
            name='Storage',
            fields=[
                ('id_file', models.AutoField(primary_key=True, serialize=False)),
                ('original_name', models.CharField(max_length=128)),
                ('new_name', models.CharField(blank=True, max_length=128, null=True)),
                ('comment', models.CharField(max_length=128)),
                ('size', models.IntegerField()),
                ('upload_date', models.DateTimeField(auto_now_add=True, db_column='uploaddate')),
                ('last_download_date', models.DateTimeField(auto_now=True, db_column='lastdownloaddate', null=True)),
                ('file', models.FileField(upload_to='uploads/')),
                ('id_user', models.ForeignKey(db_column='user_id', on_delete=django.db.models.deletion.CASCADE, related_name='storages', to='api_app.user')),
            ],
            options={
                'db_table': 'storage',
            },
        ),
    ]
