from django.urls import path
from .views import UserView, StorageView

urlpatterns = [
    path("users/", UserView.as_view(), name="users_list-add_user"),  # Для GET и POST
    path("users/<int:id_user>/", UserView.as_view(), name="user-delete_role"),  # Для DELETE и PATCH
    path("storage/<int:id_user>/", StorageView.as_view(), name='files_list-add_file'),  # Для GET и POST
    path("storage/view/<int:id_user>/<int:id_file>/", StorageView.as_view(), name='files_view'),  # Для просмотра файла
    path("storage/download/<int:id_file>/", StorageView.as_view(), name='files_download'),  # Для просмотра файла
    path("storage/link/<int:id_user>/<int:id_file>/", StorageView.as_view(), name='generate_file_link'),  # Для генерации ссылки
    path("storage/<int:id_user>/<int:id_file>/", StorageView.as_view(), name='delete_file'),  # Для удаления файла
]
