from django.contrib.auth.hashers import make_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer, StorageSerializer
from .models import User, Storage

class UserView(APIView):
    # Метод для обработки GET-запрос: получение списка всех пользователей с данными
    def get(self, request, id_user=None):
        queryset = User.objects.all()
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # Метод для обработки POST-запроса: создание нового пользователя
    def post(self, request):
        request.data["password_hash"] = make_password(request.data["password_hash"])
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Метод для обработки DELETE-запроса: удаление пользователя по ID
    def delete(self, request, **kwargs):
        id = kwargs.get("id_user")
        try:
            user = User.objects.get(id_user=id)
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response({"Детали": "Пользователь не найден."}, status=status.HTTP_404_NOT_FOUND)

    # Метод для обработки PATCH-запроса: изменение роли пользователя
    def patch(self, request, **kwargs):
        id = kwargs.get("id_user")
        if id is None:
            return Response({"Детали": "Требуется User ID."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id_user=id)
        except User.DoesNotExist:
            return Response({"Детали": "Пользователь не найден."}, status=status.HTTP_404_NOT_FOUND)

        if "role" in request.data:
            user.role = request.data["role"]
            user.save()
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({"Детали": "Неправильное поле для обновления."}, status=status.HTTP_400_BAD_REQUEST)
    