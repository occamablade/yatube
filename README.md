# Социальная сеть Yatube для публикации личных дневников (v 0.4)
![Python](https://img.shields.io/badge/Python-3.9.10-blue) ![!Django](https://img.shields.io/badge/Django-2.2.9-blue)

## Описание проекта
Социальная сеть для авторов и подписчиков. Пользователи могут подписываться на избранных авторов, оставлять и удалять комментари к постам, оставлять новые посты на главной странице и в тематических группах, прикреплять изображения к публикуемым постам.

## Для работы с проектом необходимо:

1. Клонировать репозиторий.
   ```
   git@github.com:occamablade/yatube.git
   ```
2. Cоздать и активировать виртуальное окружение:
    ```
      $ cd occamablade/yatube
      $ python -m venv venv
    ```
    Для Windows:
    ```
      $ source venv/Scripts/activate
    ```
    Для MacOs/Linux:
    ```
      $ source venv/bin/activate
    ```
3. Установить зависимости из файла requirements.txt:
    ```
    (venv) $ python -m pip install --upgrade pip
    (venv) $ pip install -r requirements.txt
    ```
4. Создать и запустить миграции:
    ```
    cd yatube/
    python manage.py makemigrations
    python manage.py migrate
    ```
5. Запустить сервер:
    ```
    python manage.py runserver
    ```
> После выполнения вышеперечисленных инструкций проект доступен по адресу http://127.0.0.1:8000/

## Контакты
**Иван Безбородников** 

[![Telegram Badge](https://img.shields.io/badge/-vanyshqa-blue?style=social&logo=telegram&link=https://t.me/vanyshqa)](https://t.me/vanyshqa) [![Gmail Badge](https://img.shields.io/badge/-bezborodnikov18@gmail.com-c14438?style=flat&logo=Gmail&logoColor=white&link=mailto:bezborodnikov18@gmail.com)](mailto:bezborodnikov18@gmail.com)
