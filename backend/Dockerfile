# Используем официальный образ Python 
FROM python:3.13.1-alpine

# Устанавливаем необходимые зависимости
# команда для полноценной версии python:
# RUN apt-get update && apt-get install -y netcat-openbsd
# команда для версии python alpine:
RUN apk update && apk add --no-cache bash

# Устанавливаем рабочую директорию 
WORKDIR /backend

# Копируем файл requirements.txt в контейнер и устанавливаем зависимости 
COPY requirements.txt /backend/
RUN pip install -r requirements.txt

# Копируем весь проект в контейнер 
COPY . /backend/

# Копировать и сделать исполняемым скрипт entrypoint
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Запускаем entrypoint скрипт
ENTRYPOINT ["/entrypoint.sh"]

# Запускаем сервер 
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"] 
