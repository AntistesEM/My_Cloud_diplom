# тестовый сервер для проверки фронтенда
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os
import jwt
import datetime

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = 'secret_key_here'

# Хранилище пользователей
users = []  # Для простоты используем список. В реальном приложении будет база данных.

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

# Хранение данных в глобальной переменной
files = [
    {
        'id': 1,
        'name': 'file1.txt',
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
]

@app.route('/api/storage', methods=['GET'])
def get_files():
    """Получение списка файлов"""
    return jsonify(files)

@app.route('/api/storage/delete/<int:file_id>', methods=['DELETE'])
def delete_file(file_id):
    """Удаление файла по его ID"""
    global files  

    # Поиск файла по ID
    file_to_delete = next((file for file in files if file['id'] == file_id), None)
    if file_to_delete is None:
        return jsonify({'error': 'Файл не найден'}), 404

    # Удаление файла из списка
    files.remove(file_to_delete)

    # Удаление файла из файловой системы
    file_path = os.path.join('uploads', file_to_delete['name'])
    if os.path.exists(file_path):
        os.remove(file_path)
    else:
        return jsonify({'error': 'Файл на диске не найден'}), 404

    return jsonify({'message': 'Файл успешно удален'}), 200

@app.route('/api/storage/upload', methods=['POST'])
def upload_file():
    """Загрузка нового файла"""
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
    if files:
        new_id = max(file['id'] for file in files) + 1
    else:
        new_id = 1  # Начальное значение для нового идентификатора

    files.append({
        'id': new_id,
        'name': file_name,
        'comment': comment,
        'size': file_size,
        'uploadDate': upload_date,
        'lastDownloadDate': upload_date  
    })

    return jsonify(files), 201

@app.route('/api/storage/rename/<int:file_id>', methods=['POST'])
def rename_file(file_id):
    """Переименование файла"""
    new_name = request.json.get('name')
    if not new_name:
        return jsonify({'error': 'Новое имя файла не указано'}), 400  

    file_to_rename = next((file for file in files if file['id'] == file_id), None)
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

@app.route('/api/storage/file/<int:file_id>', methods=['GET'])
def get_file(file_id):
    """Получение файла по ID"""
    for file in files:
        if file['id'] == file_id:
            return jsonify(file), 200  
    return jsonify({'error': 'Файл не найден'}), 404  

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

    users.append({
        'username': username,
        'fullName': fullName,
        'email': email,
        'password': hashed_password,
        'role': 'user'  # Значение по умолчанию
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
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, app.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({'token': token, 'role': user['role']}), 200

# @app.route('/api/storage', methods=['GET'])
# @token_required
# def storage(current_user):
#     # Здесь вы можете использовать данные пользователя
#     return jsonify({'message': f'Добро пожаловать, {current_user["username"]}'})

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(port=5000, debug=True)
