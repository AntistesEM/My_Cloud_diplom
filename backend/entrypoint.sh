#!/bin/bash

# Подождать, пока БД будет доступна
echo "Waiting for database to be available..."
while ! nc -z db 5432; do
	sleep 1
done

# Выполнение миграций
echo "Applying migrations..."
python manage.py migrate

# # Создание суперпользователя, если он не существует
# echo "Creating superuser..."
# if ! python manage.py createsuperuser --noinput --username admin --email admin@example.com; then
# 		echo "Superuser already exists!"
# fi


# Создание суперпользователя, если он не существует
echo "Creating superuser..."
if ! python manage.py createsuperuser --noinput --username admin --email admin@example.com; then
    echo "Superuser already exists!"
else
    # Устанавливаем пароль для суперпользователя, взятый из переменной окружения
    echo "Setting password for superuser..."
    python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); user = User.objects.get(username='admin'); user.set_password('${SUPERUSER_PASSWORD}'); user.save()"
fi

# Запуск сервера Django
echo "Starting server..."
python manage.py runserver 0.0.0.0:8000




# # Подождать, пока БД будет доступна
# echo "Waiting for database to be available..."
# until pg_isready -h db -p 5432; do
#   sleep 1
# done

# # Выполнение миграций
# echo "Applying migrations..."
# python manage.py migrate

# # Создание суперпользователя, если он не существует
# echo "Creating superuser..."
# if ! python manage.py createsuperuser --noinput --username admin --email admin@example.com; then
#     echo "Superuser already exists!"
# fi

# # Запуск сервера Django
# echo "Starting server..."
# python manage.py runserver 0.0.0.0:8000
