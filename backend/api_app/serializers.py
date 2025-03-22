from rest_framework import serializers
from .models import User, Storage

class StorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Storage
        fields = "__all__"

class UserSerializer(serializers.ModelSerializer):
    storages = StorageSerializer(many=True, read_only=True)  # связь с файлами
    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {
            "password_hash": {"write_only": True}
        }
