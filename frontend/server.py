# тестовый сервер для проверки фронтенда
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os
import jwt
import datetime

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = 'secret_key_here'

def token_required(f):
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Токен отсутствует!'}), 403
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = next((u for u in users if u['username'] == data['username']), None)
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Токен истёк!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Неправильный токен!'}), 403
        return f(current_user, *args, **kwargs)
    
    return decorated

# Хранилище пользователей
users = [
    {
        'email': "djon@mm.ru",
        'fullName': "Djonatan",
        'id': 1,
        'password': "scrypt:32768:8:1$2INmrG6tBmcsTKpF$03f0bb1d581fa2e4277236d1c40eb412b5031ee6e017816c67aaaed512bf28f2860af43f72ce9150bc321f48948b7b2c3bb531164ea5282ead5d49d199d1b224",
        'role': "admin",
        'username': "Djon",
        'storageFiles': [],
    },
    {
        'email': "ivan@jj.ru",
        'fullName': "Ivanovich",
        'id': 2,
        'password': "scrypt:32768:8:1$qoVRnZJn8uwJhQlB$fa23a420e2333a25f2eb9e1854c476e28e2fb49618036b4b0886f8da3a9dea45fa1d09f92d5405f99f6b7db6645ad114a4849b9f64b698044485005a9c5a9651",
        'role': "user",
        'username': "Ivan",
        'storageFiles': [
            {
                'id': 1,
                'name': 'file1.rar',
                'comment': 'Первый файл',
                'size': 1234,
                'uploadDate': '2023-10-01T12:00:00Z',
                'lastDownloadDate': '2023-10-02T12:00:00Z'
            },
            {
                'id': 2,
                'name': 'file2.txt',
                'comment': 'Второй файл',
                'size': 5678,
                'uploadDate': '2023-10-05T15:30:00Z',
                'lastDownloadDate': '2023-10-06T09:00:00Z'
            }
        ],
    }
]

@app.route('/api/storage/<int:user_id>', methods=['GET'])
def get_files(user_id):
    """Получение списка файлов"""
    
    # Поиск пользователя по ID
    user_current = next((user for user in users if user['id'] == user_id), None)
    if user_current is None:
        return jsonify({'error': 'Пользователь не найден'}), 404

    return jsonify(user_current['storageFiles']), 200

@app.route('/api/users', methods=['GET'])
def get_users():
    """Получение списка пользователей"""
    return jsonify(users)

@app.route('/api/storage/delete/<int:user_id>/<int:file_id>', methods=['DELETE'])
def delete_file(user_id, file_id):
    """Удаление файла по его ID"""
    
    # Поиск пользователя по ID
    user_current = next((user for user in users if user['id'] == user_id), None)
    if user_current is None:
        return jsonify({'error': 'Пользователь не найден'}), 404

    # Поиск файла по ID
    file_to_delete = next((file for file in user_current['storageFiles'] if file['id'] == file_id), None)
    if file_to_delete is None:
        return jsonify({'error': 'Файл не найден'}), 404

    # Удаление файла из списка
    user_current['storageFiles'].remove(file_to_delete)
    
    # Удаление файла из файловой системы
    file_path = os.path.join('uploads', file_to_delete['name'])
    if os.path.exists(file_path):
        os.remove(file_path)
    else:
        return jsonify({'error': 'Файл на диске не найден'}), 404

    return jsonify({'message': 'Файл успешно удален'}), 200

@app.route('/api/users/delete/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Удаление пользователя по его ID"""
    global users

    # Поиск пользователя по ID
    user_to_delete = next((user for user in users if user['id'] == user_id), None)
    if user_to_delete is None:
        return jsonify({'error': 'Пользователь не найден'}), 404

    # Удаление пользователя из списка
    users.remove(user_to_delete)
    return jsonify({'message': 'Пользователь успешно удален'}), 200

@app.route('/api/storage/upload/<int:user_id>', methods=['POST'])
def upload_file(user_id):
    """Загрузка нового файла"""

    # Поиск пользователя по ID
    user_current = next((user for user in users if user['id'] == user_id), None)
    if user_current is None:
        return jsonify({'error': 'Пользователь не найден'}), 404
    
    file = request.files.get('file')  
    comment = request.form.get('comment')  

    if file is None:
        return jsonify({'error': 'Файл не был загружен'}), 400  

    # Проверяем уникальность имени файла и генерируем новое имя, если необходимо
    file_name = file.filename
    original_file_name = file_name
    counter = 1
    while os.path.exists(os.path.join('uploads', file_name)):
        file_name = f"{os.path.splitext(original_file_name)[0]}_{counter}{os.path.splitext(original_file_name)[1]}"
        counter += 1

    file_size = len(file.read())
    file.seek(0)
    upload_date = datetime.datetime.utcnow().isoformat() + "Z"

    # Сохраняем файл на сервере
    file_path = os.path.join('uploads', file_name)
    file.save(file_path)

    # Генерируем новый ID
    if user_current['storageFiles']:
        new_id = max(file['id'] for file in user_current['storageFiles']) + 1
    else:
        new_id = 1  # Начальное значение для нового идентификатора

    user_current['storageFiles'].append({
        'id': new_id,
        'name': file_name,
        'comment': comment,
        'size': file_size,
        'uploadDate': upload_date,
        'lastDownloadDate': upload_date  
    })

    return jsonify(user_current['storageFiles']), 201

@app.route('/api/storage/rename/<int:user_id>/<int:file_id>', methods=['POST'])
def rename_file(user_id, file_id):
    """Переименование файла"""
    new_name = request.json.get('name')
    if not new_name:
        return jsonify({'error': 'Новое имя файла не указано'}), 400
    
    # Поиск пользователя по ID
    user_current = next((user for user in users if user['id'] == user_id), None)
    if user_current is None:
        return jsonify({'error': 'Пользователь не найден'}), 404

    # Поиск файла по ID
    file_to_rename = next((file for file in user_current['storageFiles'] if file['id'] == file_id), None)
    if file_to_rename is None:
        return jsonify({'error': 'Файл не найден'}), 404  

    if file_to_rename:
        old_name = file_to_rename['name']
        file_to_rename['name'] = new_name
        
        # Переименование файла в файловой системе
        old_file_path = os.path.join('uploads', old_name)
        new_file_path = os.path.join('uploads', new_name)
        if os.path.exists(old_file_path):
            os.rename(old_file_path, new_file_path)
            return jsonify(file_to_rename), 200
        else:
            return jsonify({'error': 'Файл на диске не найден'}), 404
    return jsonify({'error': 'Файл не найден'}), 404  

@app.route('/api/users/toggle/<int:user_id>', methods=['PATCH'])
def toggle_role(user_id):
    """Изменение роли"""
    new_role = request.json.get('role')
    if not new_role:
        return jsonify({'error': 'Новая роль не указана'}), 400  

    role_to_rename = next((user for user in users if user['id'] == user_id), None)
    if role_to_rename:
        role_to_rename['role'] = new_role

    return jsonify(role_to_rename), 200

@app.route('/api/storage/file/<int:user_id>/<int:file_id>', methods=['GET'])
def get_file(user_id, file_id):
    """Получение файла по ID для его просмотра"""
    
    # Поиск пользователя по ID
    user_current = next((user for user in users if user['id'] == user_id), None)
    if user_current is None:
        return jsonify({'error': 'Пользователь не найден'}), 404

    # Поиск файла по ID
    file_to_view = next((file for file in user_current['storageFiles'] if file['id'] == file_id), None)
    if file_to_view is None:
        return jsonify({'error': 'Файл не найден'}), 404

    # Путь к файлу
    file_path = os.path.join('uploads', file_to_view['name'])
    
    # Проверка существования файла
    if not os.path.exists(file_path):
        return jsonify({'error': 'Файл не найден на сервере'}), 404

    # Возврат файла для просмотра или загрузки
    return send_from_directory(directory='uploads', path=file_to_view['name'], as_attachment=False)
    
    # return jsonify(file_to_view), 200  

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    fullName = data.get('fullName')
    email = data.get('email')
    password = data.get('password')

    if not username or not fullName or not email or not password:
        return jsonify({'message': 'Все поля должны быть заполнены!'}), 400

    if any(user['username'] == username for user in users):
        return jsonify({'message': 'Пользователь с таким именем уже существует!'}), 400

    # Хеширование пароля
    hashed_password = generate_password_hash(password)

    # Генерируем новый ID
    if users:
        user_id = max(user['id'] for user in users) + 1
    else:
        user_id = 1  # Начальное значение для нового идентификатора

    users.append({
        'id': user_id,
        'username': username,
        'fullName': fullName,
        'email': email,
        'password': hashed_password,
        'role': 'user',  # Значение по умолчанию
        'storageFiles': [],
    })
    return jsonify({'message': 'Регистрация прошла успешно!'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = next((u for u in users if u['username'] == username), None)
    if not user or not check_password_hash(user['password'], password):
        return jsonify({'message': 'Неверные имя пользователя или пароль!'}), 401

    # Генерация токена
    token = jwt.encode({
        'username': username,
        'role': user['role'],
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
    }, app.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({'token': token, 'role': user['role'], 'id': user['id']}), 200

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(port=5000, debug=True)
