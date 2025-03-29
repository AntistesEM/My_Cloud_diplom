
from rest_framework.permissions import BasePermission

class IsAuthenticatedOrViewFile(BasePermission):
    """
    Позволяет доступ к методу view_file без аутентификации, 
    и требует аутентификацию для остальных методов.
    """
    def has_permission(self, request, view):
        # Проверяем, если метод view_file вызывается через GET-запрос
        if request.method == 'GET':
            id_user = view.kwargs.get('id_user')
            id_file = view.kwargs.get('id_file')

            # Проверка, что был передан id_user и id_file - это условия для использования `view_file`
            if id_user and id_file:
                return True  # Разрешаем, если это метод view_file

        # Если не view_file, проверяем аутентификацию
        return request.user.is_authenticated