import datetime
import django.urls
import mimetypes
import os
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.http import FileResponse, Http404, HttpResponse, StreamingHttpResponse
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import urllib.parse
from .serializers import UserSerializer, StorageSerializer
from .models import User, Storage
import logging

logger = logging.getLogger(__name__)

class UserView(APIView):
    # Метод для обработки GET-запрос: получение списка всех пользователей с данными
    def get(self, request, id_user=None):
        queryset = User.objects.all()
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Метод для обработки POST-запроса: создание нового пользователя или вход в личный кабинет
    def post(self, request):
        if 'email' not in request.data:
            # вход в личный кабинет
            return self.login_user(request)
        else:
            # создание нового пользователя
            return self.create_user(request)

    def create_user(self, request):
        request.data["password_hash"] = make_password(request.data["password_hash"])
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def login_user(self, request):
        try:
            user = User.objects.get(username=request.data["username"])
        except User.DoesNotExist:
            return Response({"Детали": "Пользователь не найден."}, status=status.HTTP_404_NOT_FOUND)

        if user.check_password(request.data["password_hash"]):
            # Генерация токена
            refresh = RefreshToken.for_user(user)
            serializer = UserSerializer(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'id_user': user.id_user,
                'role': user.role
            }, status=status.HTTP_200_OK)
        else:
            return Response({"Детали": "Неправильный пароль."}, status=status.HTTP_401_UNAUTHORIZED)

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

class StorageView(APIView):
    # Метод для обработки GET-запроса: получение списка всех файлов пользователя
    def get(self, request, id_user=None, id_file=None):
        if id_user and id_file:
            # просмотр файла
            return self.view_get(request, id_user, id_file)
        elif id_file:
            # скачивание файла
            return self.download_file(request, id_file)
        else:
            # получение списка всех файлов
            queryset = Storage.objects.filter(id_user=id_user)
            serializer = StorageSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    # # Метод для просмотра файла
    # def view_get(self, request, id_user, id_file):
    #     return self.send_file_response(request, id_file, inline=True)

    # Новый метод для скачивания файла
    # def download_file(self, request, id_file):
    #     return self.send_file_response(request, id_file, inline=False)

    # # Универсальный метод для отправки файла
    # def send_file_response(self, request, id_file, inline=True):
    #     try:
    #         file_view = Storage.objects.get(id_file=id_file)
    #         file_path = file_view.file.path

    #         if not os.path.exists(file_path):
    #             raise Http404("Файл не найден")

    #         # Получаем MIME-тип файла
    #         content_type, _ = mimetypes.guess_type(file_path)

    #         # Если MIME-тип не удалось определить, устанавливаем значение по умолчанию
    #         if content_type is None:
    #             content_type = 'application/octet-stream'

    #         # Для всех типов файлов, используем FileResponse
    #         response = FileResponse(open(file_path, 'rb'), content_type=content_type)

    #         # Задаем заголовок Content-Disposition
    #         disposition_type = 'attachment' if not inline else 'inline'
    #         response['Content-Disposition'] = f'{disposition_type}; filename="{file_view.original_name}"'

    #         return response
    #     except Storage.DoesNotExist:
    #         raise Http404("Файл не найден")

    # Метод для обработки GET-запроса: просмотр файла
    def view_get(self, request, id_user, id_file):  # ! исправить проблему с русскими символами с помощью кодирования
        try:
            file_view = Storage.objects.get(id_file=id_file)
            file_path = file_view.file.path

            if not os.path.exists(file_path):
                raise Http404("Файл не найден")

            # Получаем MIME-тип файла
            content_type, _ = mimetypes.guess_type(file_path)
            
            # Если MIME-тип не удалось определить, устанавливаем значение по умолчанию
            if content_type is None:
                content_type = 'application/octet-stream'

            # Если файл текстовый, открываем его с кодировкой
            if content_type in ['text/plain', 'text/html', 'text/csv']:
                with open(file_path, 'r', encoding='utf-8') as file:
                    response = HttpResponse(file.read(), content_type=f"{content_type}; charset=utf-8")
            else:
                # Для остальных типов файлов, используем FileResponse
                response = FileResponse(open(file_path, 'rb'), content_type=content_type)

            response['Content-Disposition'] = f'inline; filename="{file_view.original_name}"'
            return response
        except Storage.DoesNotExist:
            raise Http404("Файл не найден")
    def download_file(self, request, id_file):
        try:
            uploaded_file = Storage.objects.get(id_file=id_file)
            file_path = uploaded_file.file.path
            
            content_type, _ = mimetypes.guess_type(file_path)
            if content_type is None:
                content_type = 'application/octet-stream'
            
            def file_iterator(file_name, chunk_size=512):
                with open(file_name, 'rb') as f:
                    while True:
                        chunk = f.read(chunk_size)
                        if not chunk:
                            break
                        yield chunk
            
            # Кодируем имя файла для корректной обработки специальными символами(русских букв в названии)
            encoded_file_name = urllib.parse.quote(uploaded_file.original_name)

            response = StreamingHttpResponse(file_iterator(file_path), content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{encoded_file_name}"'
            return response
        
        except Storage.DoesNotExist:
            raise Http404("Файл не найден")

        # # работает
        # uploaded_file = Storage.objects.get(id_file=id_file)
        # file_path = uploaded_file.file.path
        # with open(file_path, 'rb') as file_handle:
        #     content_type, _ = mimetypes.guess_type(file_path)
        #     if content_type is None:  # Если MIME-тип не удается определить
        #         content_type = 'application/octet-stream'  # Устанавливаем значение по умолчанию
            
        #     # Кодируем имя файла для корректной обработки специальными символами(русских букв в названии)
        #     encoded_file_name = urllib.parse.quote(uploaded_file.original_name)
            
        #     response = HttpResponse(file_handle.read(), content_type=content_type)
        #     response['Content-Disposition'] = f'attachment; filename="{encoded_file_name}"'
        #     return response
        
        # uploaded_file = Storage.objects.get(id_file=id_file)        
        # Открываем файл на чтение в бинарном режиме
        # file_path = uploaded_file.file.path
        # with open(file_path, 'rb') as fh:
        #     # Отправка файла
        #     response = HttpResponse(fh.read(), content_type='application/force-download')
        #     response['Content-Disposition'] = f'attachment; filename="{uploaded_file.original_name}"'  # Используем оригинальное название файла
        #     return response
        
        
        # uploaded_file = Storage.objects.get(id_file=id_file)
        # content_type, _ = mimetypes.guess_type(uploaded_file.file.path)
        # if content_type is None:  # Если MIME-тип не удается определить
        #     content_type = 'application/octet-stream'  
        # response = HttpResponse(uploaded_file.file, content_type=content_type)
        # response['Content-Disposition'] = f'attachment; filename="{uploaded_file.original_name}"'
        # return response

    # Метод для обработки POST-запроса: загрузка нового файла
    def post(self, request, id_user, id_file=None):
        if 'file' not in request.data:
            pass

        else:
            # загрузка файла
            return self.upload_file(request, id_user)

    # Метод для обработки PATCH-запроса: переименование файла
    def patch(self, request, id_user, id_file):
        new_name = request.data["name"]
        # Проверяем, существует ли файл с таким именем
        if os.path.exists(os.path.join(settings.MEDIA_ROOT, "uploads", new_name)):
            return Response({"Детали": "Файл с таким именем уже существует"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            file_to_rename = Storage.objects.get(id_file=id_file)
            old_file_path = file_to_rename.file.path
            new_file_path = os.path.join(os.path.dirname(old_file_path), new_name.replace(" ", "_"))
            os.rename(old_file_path, new_file_path)
            file_to_rename.original_name = new_name
            file_to_rename.file.name = os.path.join('uploads', new_name.replace(" ", "_"))
            file_to_rename.new_name = None
            file_to_rename.save()
            serializer = StorageSerializer(file_to_rename)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Storage.DoesNotExist:
            return Response({"Детали": f"Файл с указанным id_file = {id_file} не существует в базе данных"}, status=status.HTTP_404_NOT_FOUND)
        except FileNotFoundError:
            return Response({"Детали": "Файл для переименования не найден на файловой системе"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"Детали": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Метод для загрузки нового файла
    def upload_file(self, request, id_user):
        file = request.data["file"]
        comment = request.data["comment"]
        
        try:
            user = User.objects.get(id_user=id_user)
        except User.DoesNotExist:
            return Response({"Детали": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)

        # # Проверка на максимальный размер файла для size = models.IntegerField()
        # MAX_SIZE = 2_147_483_647  # Максимальный размер для 32-битного IntegerField
        # if file.size > MAX_SIZE:
        #     return Response({"Детали": "Файл слишком большой"}, status=status.HTTP_400_BAD_REQUEST)

        # Сохраняем файл и информацию о файле в базе данных
        storage_file = Storage(
            id_user=user,
            original_name=file.name,
            comment=comment,
            size=file.size,
            file=file
        )
        storage_file.save()

        if file.name.replace(' ', '_') != storage_file.file.name.split('/')[-1]:
            new_name = storage_file.file.name.split('/')[-1]  # Получаем имя файла без пути
            print(f"Файл {file.name} уже существует. Изменяем его на {new_name}")
            storage_file.new_name = new_name
            storage_file.save()
        # return Response({"Детали": "Файл загружен"}, status=status.HTTP_201_CREATED)
        return self.get(request, id_user)
        
    # Метод для обработки DELETE-запроса: удаление пользователя по ID
    def delete(self, request, id_user, id_file):
        
        try:
            file = Storage.objects.get(id_user=id_user, id_file=id_file)
            file.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Storage.DoesNotExist:
            return Response({"Детали": "Файл не найден."}, status=status.HTTP_404_NOT_FOUND)
