from django.db import models

class User(models.Model):
    id_user = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=128, unique=True, null=False)
    username = models.CharField(max_length=128, unique=True, null=False)
    fullname = models.CharField(max_length=128, null=False)
    role = models.CharField(max_length=128, default="user")
    password_hash = models.CharField(max_length=128, null=False)

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.username


class Storage(models.Model):
    id_storage = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="storages", db_column="user_id")
    original_name = models.CharField(max_length=128, null=False)
    new_name = models.CharField(max_length=128, null=True, blank=True)
    comment = models.CharField(max_length=128, null=False)
    size = models.IntegerField()
    upload_date = models.DateTimeField(db_column="uploaddate")
    last_download_date = models.DateTimeField(null=True, blank=True, db_column="lastdownloaddate")

    class Meta:
        db_table = "storage"

    def __str__(self):
        return self.original_name
