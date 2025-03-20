import os
from django.db import models
from django.contrib.auth.hashers import check_password

class User(models.Model):
    id_user = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=128, unique=True, null=False)
    username = models.CharField(max_length=128, unique=True, null=False)
    fullname = models.CharField(max_length=128, null=False)
    role = models.CharField(max_length=128, default="user")
    password_hash = models.CharField(max_length=128, null=False)

    class Meta:
        db_table = "users"

    def check_password(self, raw_password):
        return check_password(raw_password, self.password_hash)

    def __str__(self):
        return self.username

class Storage(models.Model):
    id_file = models.AutoField(primary_key=True)
    id_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="storages", db_column="user_id")
    original_name = models.CharField(max_length=128, null=False)
    new_name = models.CharField(max_length=128, null=True, blank=True)
    comment = models.CharField(max_length=128, null=False)
    size = models.BigIntegerField()
    upload_date = models.DateTimeField(auto_now_add=True, db_column="uploaddate")
    last_download_date = models.DateTimeField(null=True, auto_now=True, blank=True, db_column="lastdownloaddate")
    file = models.FileField(upload_to='uploads/')

    class Meta:
        db_table = "storage"

    def __str__(self):
        return self.original_name

    def delete(self, *args, **kwargs):
        # Удаляем файл из файловой системы
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        super(Storage, self).delete(*args, **kwargs)
