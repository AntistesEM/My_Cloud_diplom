from django.urls import path
from .views import UserView

urlpatterns = [
    path("users/", UserView.as_view(), name="users_list-add_user"),  # Для GET и POST
    path("users/<int:id_user>/", UserView.as_view(), name="user-delete_role"),  # Для DELETE и PATCH
]
