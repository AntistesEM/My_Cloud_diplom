# import mimetypes
# import os
# from django.conf import settings
# from django.http import FileResponse, Http404, HttpResponse, StreamingHttpResponse
# from django.views import View
# from django.utils.crypto import get_random_string
# from django.utils import timezone
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.exceptions import AuthenticationFailed
# from rest_framework.permissions import AllowAny, IsAuthenticated
# import urllib.parse
# from .serializers import UserSerializer, StorageSerializer
# from .models import User, Storage
# from .permissions import IsAuthenticatedOrViewFile
# import logging

# logger = logging.getLogger(__name__)

# class UserView(APIView):
#     permission_classes = [AllowAny]
#     # Метод для обработки GET-запрос: получение списка всех пользователей с данными или получение данных о пользователе по токену
#     def get(self, request, id_user=None):
#         if request.path == '/api/users/user_info/':
#             return self.get_user_info(request)
        
#         queryset = User.objects.all()
#         serializer = UserSerializer(queryset, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)
        
#     def get_user_info(self, request):
#         self.permission_classes = [IsAuthenticated]
#         self.check_permissions(request)

#         user = request.user
#         user_data = {
#             'id_user': user.id_user,
#             'email': user.email,
#             'username': user.username,
#             'fullname': user.fullname,
#             'role': user.role,
#             'is_active': user.is_active,
#             'is_staff': user.is_staff,
#         }
#         return Response(user_data)

#     # Метод для обработки POST-запроса: создание нового пользователя, вход и выход в(из) личного кабинета
#     def post(self, request):
#         if len(request.data) == 1 and 'username' :     
#             # вход в личный кабинет
#             return self.login_user(request)
#         elif 'password' in request.data:
#             # создание нового пользователя
#             return self.create_user(request)
#         else:
#             # выход из личного кабинета
#             return self.logout(request)

#     def logout(self, request):        
#         self.permission_classes = [IsAuthenticated]
#         self.check_permissions(request)
#         request.user.auth_token.delete()
#         return Response(status=204)

#     def create_user(self, request):
#         serializer = UserSerializer(data=request.data)
#         if serializer.is_valid():
#             user = serializer.save()
#             return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def login_user(self, request):        
#         self.permission_classes = [IsAuthenticated]
#         try:
#             self.check_permissions(request)
#             user = User.objects.get(username=request.data["username"])
#         except AuthenticationFailed:
#             return Response({"detail": "Не авторизован."}, status=status.HTTP_401_UNAUTHORIZED)
#         except User.DoesNotExist:
#             return Response({"detail": "Пользователь не найден."}, status=status.HTTP_404_NOT_FOUND)
#         else:
#             return Response({
#                 'id_user': user.id_user,
#                 'role': user.role
#             }, status=status.HTTP_200_OK)

#     # Метод для обработки DELETE-запроса: удаление пользователя по ID
#     def delete(self, request, **kwargs):
#         self.permission_classes = [IsAuthenticated]
#         self.check_permissions(request)
#         id = kwargs.get("id_user")
#         try:
#             user = User.objects.get(id_user=id)
#             user.delete()
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         except User.DoesNotExist:
#             return Response({"detail": "Пользователь не найден."}, status=status.HTTP_404_NOT_FOUND)

#     # Метод для обработки PATCH-запроса: изменение роли пользователя
#     def patch(self, request, **kwargs):
#         self.permission_classes = [IsAuthenticated]
#         self.check_permissions(request)
#         id = kwargs.get("id_user")
#         if id is None:
#             return Response({"detail": "Требуется User ID."}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             user = User.objects.get(id_user=id)
#         except User.DoesNotExist:
#             return Response({"detail": "Пользователь не найден."}, status=status.HTTP_404_NOT_FOUND)
        
#         if "role" in request.data:
#             user.role = request.data["role"]
#             user.save()
#             serializer = UserSerializer(user)
#             return Response(serializer.data, status=status.HTTP_200_OK)

#         return Response({"detail": "Неправильное поле для обновления."}, status=status.HTTP_400_BAD_REQUEST)


# class ViewFile(View):
#     def get(self, request, id_user, id_file):
#         try:
#             file = Storage.objects.get(id_file=id_file, id_user_id=id_user)
#             file_path = file.file.path

#             if os.path.exists(file_path):
#                 # Определяем заголовки
#                 response = HttpResponse(open(file_path, 'rb'), content_type='application/octet-stream')
                
#                 # Установка правильного имени файла для скачивания
#                 response['Content-Disposition'] = f'inline; filename="{file.original_name}"'
#                 return response
#             else:
#                 raise Http404("Файл не найден")
        
#         except Storage.DoesNotExist:
#             raise Http404("Файл не существует")
        

# class StorageView(APIView):
#     permission_classes = [IsAuthenticatedOrViewFile]

    
#     # Метод для Обновления поля last_download_date
#     def update_last_download_date(self, file: Storage):
#         file.last_download_date = timezone.now()
#         file.save(update_fields=['last_download_date'])

#     # Метод для очистки истекших токенов для специальных ссылок
#     def clean_expired_tokens(self):
#         now = timezone.now()
#         objects = Storage.objects.filter(token_expiration__lt=now)
#         # Обновляем истекшие токены, очищая поля token и token_expiration
#         if objects:
#             objects.update(token=None, token_expiration=None)

#     # Метод для обработки GET-запроса: получение списка всех файлов пользователя, просмотр файла, скачивание файла
#     def get(self, request, id_user=None, id_file=None, token=None):
#         if id_user and id_file:
#             # просмотр файла
#             return self.view_file(request, id_user, id_file)
#         elif id_file:
#             # скачивание файла
#             return self.download_file(request, id_file)
#         elif token:
#             # скачивание файла по токену(специальной ссылке)
#             return self.download_file_by_token(request, token)
#         else:
#             self.clean_expired_tokens()  # удаляем истекшие ссылки
#             # получение списка всех файлов
#             queryset = Storage.objects.filter(id_user=id_user)
#             serializer = StorageSerializer(queryset, many=True)
#             return Response(serializer.data, status=status.HTTP_200_OK)

#     # Метод для обработки GET-запроса: просмотр файла    
#     def view_file(self, request, id_user, id_file):
#         try:
#             file_view = Storage.objects.get(id_file=id_file)
#             file_path = file_view.file.path

#             if not os.path.exists(file_path):
#                 raise Http404("Файл не найден")

#             # Получаем MIME-тип файла
#             content_type, _ = mimetypes.guess_type(file_path)
            
#             # Если MIME-тип не удалось определить, устанавливаем значение по умолчанию
#             if content_type is None:
#                 content_type = 'application/octet-stream'

#             # Если файл текстовый, открываем его с кодировкой
#             if content_type in ['text/plain', 'text/html', 'text/csv']:
#                 with open(file_path, 'r', encoding='utf-8') as file:
#                     response = HttpResponse(file.read(), content_type=f"{content_type}; charset=utf-8")
#             else:
#                 # Для остальных типов файлов, используем FileResponse
#                 response = FileResponse(open(file_path, 'rb'), content_type=content_type)

#             encoded_file_name = urllib.parse.quote(file_view.original_name)
#             response['Content-Disposition'] = f'inline; filename="{encoded_file_name}"'
#             return response
#         except Storage.DoesNotExist:
#             raise Http404("Файл не найден")
        
#     # Вариант 2:работает но 2 проблемы:
#     # 1. не отображает нормально русские буквы в txt файлах, 
#     # 2. если браузер не поддерживает просмотр то скачивает файл, но под непонятным именем
#     # def view_file(self, request, id_user, id_file):
#     #     storage = get_object_or_404(Storage, id_user=id_user, id_file=id_file)
#     #     file_path = storage.file.path

#     #     # Определяем тип контента файла
#     #     content_type = mimetypes.guess_type(file_path)[0]
#     #     print("content_type", content_type)
#     #     if content_type is None:
#     #         content_type = 'application/octet-stream'
#     #     print("content_type", content_type, type(content_type))

#     #     # Открываем файл и отправляем его содержимое в ответ
#     #     with open(file_path, 'rb') as file:
#     #         encoded_file_name = urllib.parse.quote(storage.original_name)
#     #         response = HttpResponse(file, content_type=content_type)
#     #         response['Content-Disposition'] = f'inline; filename="{encoded_file_name}"'
#     #         return response
        
#     # Метод для обработки GET-запроса: скачивание файла
#     def download_file(self, request, id_file):
#         try:
#             uploaded_file = Storage.objects.get(id_file=id_file)
#             file_path = uploaded_file.file.path            
#             content_type, _ = mimetypes.guess_type(file_path)
#             if content_type is None:
#                 content_type = 'application/octet-stream'            

#             def file_iterator(file_name, chunk_size=512):
#                 with open(file_name, 'rb') as f:
#                     while True:
#                         chunk = f.read(chunk_size)
#                         if not chunk:
#                             break
#                         yield chunk
#             encoded_file_name = urllib.parse.quote(uploaded_file.original_name)

#             # Обновляем поле last_download_date
#             self.update_last_download_date(uploaded_file)

#             response = StreamingHttpResponse(file_iterator(file_path), content_type=content_type)
#             response['Content-Disposition'] = f'attachment; filename="{encoded_file_name}"'
#             response['X-Filename'] = encoded_file_name
            
#             response['X-Last-Download-Date'] = uploaded_file.last_download_date.isoformat()
#             return response
#         except Storage.DoesNotExist:
#             return HttpResponse(status=404)
    
#     # Метод к GET-запросу: скачивание файла по ссылке
#     def download_file_by_token(self, request, token):
#         try:
#             # Получаем файл по токену
#             storage_item = Storage.objects.get(token=token)

#             # Проверяем, не истек ли токен
#             if storage_item.token_expiration < timezone.now():
#                 return Response({"detail": "Ссылка устарела."}, status=status.HTTP_403_FORBIDDEN)

#             file_path = storage_item.file.path

#             if not os.path.exists(file_path):
#                 raise Http404("Файл не найден")

#             content_type, _ = mimetypes.guess_type(file_path)
#             if content_type is None:
#                 content_type = 'application/octet-stream'
                
#             def file_iterator(file_name, chunk_size=512):
#                 with open(file_name, 'rb') as f:
#                     while True:
#                         chunk = f.read(chunk_size)
#                         if not chunk:
#                             break
#                         yield chunk

#             encoded_file_name = urllib.parse.quote(storage_item.original_name)

#             # Обновляем поле last_download_date
#             self.update_last_download_date(storage_item)

#             response = StreamingHttpResponse(file_iterator(file_path), content_type=content_type)
#             response['Content-Disposition'] = f'attachment; filename="{encoded_file_name}"'
#             response['X-Filename'] = encoded_file_name
#             return response

#         except Storage.DoesNotExist:
#             return Response({"detail": "Файл не найден."}, status=status.HTTP_404_NOT_FOUND)

#     # Метод для обработки POST-запроса: загрузка нового файла, генерации ссылки
#     def post(self, request, id_user=None, id_file=None):
#         if id_file and id_user:
#             # генерация ссылки
#             return self.generate_file_link(request, id_user, id_file)
#         else:
#             # загрузка файла
#             return self.upload_file(request, id_user)

#     def generate_file_link(self, request, id_user, id_file):
#         '''
#         Генерирует уникальную ссылку для доступа к файлу
#         '''
#         # Проверяем, существует ли файл
#         try:
#             storage_item = Storage.objects.get(id_file=id_file, id_user=id_user)
#         except Storage.DoesNotExist:
#             return Response({"detail": "Файл не найден."}, status=status.HTTP_404_NOT_FOUND)

#         # Генерируем уникальный токен
#         unique_token = get_random_string(length=32)

#         # Сохраняем токен
#         storage_item.token = unique_token
#         storage_item.token_expiration = timezone.now() + timezone.timedelta(minutes=5)
#         storage_item.save()

#         # Формируем ссылку
#         link = request.build_absolute_uri(f"/api/storage/download/{unique_token}/")

#         return Response({"link": link}, status=status.HTTP_200_OK)
    
#     # Метод к POST-запросу: загрузка нового файла
#     def upload_file(self, request, id_user):
#         file = request.data["file"]
#         comment = request.data["comment"]
        
#         try:
#             user = User.objects.get(id_user=id_user)
#         except User.DoesNotExist:
#             return Response({"detail": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)

#         # Сохраняем файл и информацию о файле в базе данных
#         storage_file = Storage(
#             id_user=user,
#             original_name=file.name,
#             comment=comment,
#             size=file.size,
#             file=file
#         )
#         storage_file.save()

#         if file.name.replace(' ', '_') != storage_file.file.name.split('/')[-1]:
#             new_name = storage_file.file.name.split('/')[-1]  # Получаем имя файла без пути
#             print(f"Файл {file.name} уже существует. Изменяем его на {new_name}")
#             storage_file.new_name = new_name
#             storage_file.save()
#         return self.get(request, id_user)
    
#     # Метод для обработки PATCH-запроса: переименование файла
#     def patch(self, request, id_user, id_file):
#         new_name = request.data["name"]
#         # Проверяем, существует ли файл с таким именем
#         if os.path.exists(os.path.join(settings.MEDIA_ROOT, "uploads", new_name)):
#             return Response({"detail": "Файл с таким именем уже существует"}, status=status.HTTP_400_BAD_REQUEST)        
#         try:
#             file_to_rename = Storage.objects.get(id_file=id_file)
#             old_file_path = file_to_rename.file.path
#             new_file_path = os.path.join(os.path.dirname(old_file_path), new_name.replace(" ", "_"))
#             os.rename(old_file_path, new_file_path)
#             file_to_rename.original_name = new_name
#             file_to_rename.file.name = os.path.join('uploads', new_name.replace(" ", "_"))
#             file_to_rename.new_name = None
#             file_to_rename.save()
#             serializer = StorageSerializer(file_to_rename)

#             return Response(serializer.data, status=status.HTTP_200_OK)
#         except Storage.DoesNotExist:
#             return Response({"detail": f"Файл с указанным id_file = {id_file} не существует в базе данных"}, status=status.HTTP_404_NOT_FOUND)
#         except FileNotFoundError:
#             return Response({"detail": "Файл для переименования не найден на файловой системе"}, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#     # Метод для обработки DELETE-запроса: удаление файла по ID
#     def delete(self, request, id_user, id_file):        
#         try:
#             file = Storage.objects.get(id_user=id_user, id_file=id_file)
#             file.delete()
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         except Storage.DoesNotExist:
#             return Response({"Детали": "Файл не найден."}, status=status.HTTP_404_NOT_FOUND)


import mimetypes
import os
from django.conf import settings
from django.http import FileResponse, Http404, HttpResponse, StreamingHttpResponse
from django.views import View
from django.utils.crypto import get_random_string
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny, IsAuthenticated
import urllib.parse
from .serializers import UserSerializer, StorageSerializer
from .models import User, Storage
from .permissions import IsAuthenticatedOrViewFile

class UserView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, id_user=None):
        if request.path == '/api/users/user_info/':
            return self.get_user_info(request)
        return self.get_all_users()

    def get_all_users(self):
        queryset = User.objects.all()
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_user_info(self, request):
        self.check_permissions(request)
        user = request.user
        user_data = {
            'id_user': user.id_user,
            'email': user.email,
            'username': user.username,
            'fullname': user.fullname,
            'role': user.role,
            'is_active': user.is_active,
            'is_staff': user.is_staff,
        }
        return Response(user_data)

    def post(self, request):
        if 'username' in request.data and len(request.data) == 1:
            return self.login_user(request)
        elif 'password' in request.data:
            return self.create_user(request)
        return self.logout(request)

    def logout(self, request):
        self.check_permissions(request)
        request.user.auth_token.delete()
        return Response(status=204)

    def create_user(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def login_user(self, request):
        self.check_permissions(request)
        try:
            user = User.objects.get(username=request.data["username"])
        except User.DoesNotExist:
            return Response({"detail": "Пользователь не найден."}, status=status.HTTP_404_NOT_FOUND)
        return Response({'id_user': user.id_user, 'role': user.role}, status=status.HTTP_200_OK)

    def delete(self, request, **kwargs):
        self.check_permissions(request)
        id_user = kwargs.get("id_user")
        try:
            user = User.objects.get(id_user=id_user)
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response({"detail": "Пользователь не найден."}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, **kwargs):
        self.check_permissions(request)
        id_user = kwargs.get("id_user")
        if id_user is None:
            return Response({"detail": "Требуется User ID."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id_user=id_user)
        except User.DoesNotExist:
            return Response({"detail": "Пользователь не найден."}, status=status.HTTP_404_NOT_FOUND)
        if "role" in request.data:
            user.role = request.data["role"]
            user.save()
            return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
        return Response({"detail": "Неправильное поле для обновления."}, status=status.HTTP_400_BAD_REQUEST)

class ViewFile(APIView):
    def get(self, request, id_user, id_file):
        try:
            file = Storage.objects.get(id_file=id_file, id_user_id=id_user)
            return self.serve_file(file)
        except Storage.DoesNotExist:
            raise Http404("Файл не существует")

    def serve_file(self, file):
        file_path = file.file.path
        if os.path.exists(file_path):
            response = HttpResponse(open(file_path, 'rb'), content_type='application/octet-stream')
            response['Content-Disposition'] = f'inline; filename="{file.original_name}"'
            return response
        raise Http404("Файл не найден")

class StorageView(APIView):
    permission_classes = [IsAuthenticated]

    def update_last_download_date(self, file: Storage):
        file.last_download_date = timezone.now()
        file.save(update_fields=['last_download_date'])

    def clean_expired_tokens(self):
        now = timezone.now()
        Storage.objects.filter(token_expiration__lt=now).update(token=None, token_expiration=None)

    def get(self, request, id_user=None, id_file=None, token=None):
        if id_user and id_file:
            return self.view_file(request, id_user, id_file)
        elif id_file:
            return self.download_file(request, id_file)
        elif token:
            return self.download_file_by_token(request, token)
        self.clean_expired_tokens()
        return self.get_user_files(request, id_user)

    def get_user_files(self, request, id_user):
        queryset = Storage.objects.filter(id_user=id_user)
        serializer = StorageSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def view_file(self, request, id_user, id_file):
        try:
            file_view = Storage.objects.get(id_file=id_file)
            return self.serve_file(file_view)
        except Storage.DoesNotExist:
            raise Http404("Файл не найден")

    def download_file(self, request, id_file):
        try:
            uploaded_file = Storage.objects.get(id_file=id_file)
            return self.serve_file_for_download(uploaded_file)
        except Storage.DoesNotExist:
            return HttpResponse(status=404)

    def serve_file_for_download(self, uploaded_file):
        file_path = uploaded_file.file.path
        content_type, _ = mimetypes.guess_type(file_path)
        content_type = content_type or 'application/octet-stream'
        self.update_last_download_date(uploaded_file)
        response = StreamingHttpResponse(self.file_iterator(file_path), content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{urllib.parse.quote(uploaded_file.original_name)}"'
        return response

    def file_iterator(self, file_name, chunk_size=512):
        with open(file_name, 'rb') as f:
            while chunk := f.read(chunk_size):
                yield chunk

    def download_file_by_token(self, request, token):
        try:
            storage_item = Storage.objects.get(token=token)
            if storage_item.token_expiration < timezone.now():
                return Response({"detail": "Ссылка устарела."}, status=status.HTTP_403_FORBIDDEN)
            return self.serve_file_for_download(storage_item)
        except Storage.DoesNotExist:
            return Response({"detail": "Файл не найден."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, id_user=None, id_file=None):
        if id_file and id_user:
            return self.generate_file_link(request, id_user, id_file)
        return self.upload_file(request, id_user)

    def generate_file_link(self, request, id_user, id_file):
        try:
            storage_item = Storage.objects.get(id_file=id_file, id_user=id_user)
            unique_token = get_random_string(length=32)
            storage_item.token = unique_token
            storage_item.token_expiration = timezone.now() + timezone.timedelta(seconds=10)
            storage_item.save()
            link = request.build_absolute_uri(f"/api/storage/download/{unique_token}/")
            return Response({"link": link}, status=status.HTTP_200_OK)
        except Storage.DoesNotExist:
            return Response({"detail": "Файл не найден."}, status=status.HTTP_404_NOT_FOUND)

    def upload_file(self, request, id_user):
        file = request.data["file"]
        comment = request.data["comment"]
        try:
            user = User.objects.get(id_user=id_user)
            storage_file = Storage(id_user=user, original_name=file.name, comment=comment, size=file.size, file=file)
            storage_file.save()
            self.handle_file_name_conflict(storage_file, file)
            return self.get(request, id_user)
        except User.DoesNotExist:
            return Response({"detail": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)

    def handle_file_name_conflict(self, storage_file, file):
        if file.name.replace(' ', '_') != storage_file.file.name.split('/')[-1]:
            new_name = storage_file.file.name.split('/')[-1]
            print(f"Файл {file.name} уже существует. Изменяем его на {new_name}")
            storage_file.new_name = new_name
            storage_file.save()

    def patch(self, request, id_user, id_file):
        new_name = request.data["name"]
        if os.path.exists(os.path.join(settings.MEDIA_ROOT, "uploads", new_name)):
            return Response({"detail": "Файл с таким именем уже существует"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            file_to_rename = Storage.objects.get(id_file=id_file)
            self.rename_file(file_to_rename, new_name)
            return Response(StorageSerializer(file_to_rename).data, status=status.HTTP_200_OK)
        except Storage.DoesNotExist:
            return Response({"detail": f"Файл с указанным id_file = {id_file} не существует в базе данных"}, status=status.HTTP_404_NOT_FOUND)
        except FileNotFoundError:
            return Response({"detail": "Файл для переименования не найден на файловой системе"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def rename_file(self, file_to_rename, new_name):
        old_file_path = file_to_rename.file.path
        new_file_path = os.path.join(os.path.dirname(old_file_path), new_name.replace(" ", "_"))
        os.rename(old_file_path, new_file_path)
        file_to_rename.original_name = new_name
        file_to_rename.file.name = os.path.join('uploads', new_name.replace(" ", "_"))
        file_to_rename.new_name = None
        file_to_rename.save()

    def delete(self, request, id_user, id_file):
        try:
            file = Storage.objects.get(id_user=id_user, id_file=id_file)
            file.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Storage.DoesNotExist:
            return Response({"detail": "Файл не найден."}, status=status.HTTP_404_NOT_FOUND)
