from django.contrib import admin
from .models import User, Storage

# Настраиваем отображение модели User
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'fullname', 'role')  # Поля для отображения в списке
    search_fields = ('username', 'email')  # Поля для поиска

# Настраиваем отображение модели Storage
class StorageAdmin(admin.ModelAdmin):
    list_display = ('original_name', 'id_user', 'size', 'upload_date')  # Поля для отображения в списке
    list_filter = ('id_user', 'upload_date')  # Фильтры для интерфейса
    search_fields = ('original_name', 'id_user__username')  # Поля для поиска

# Регистрируем модели
admin.site.register(User, UserAdmin)
admin.site.register(Storage, StorageAdmin)
