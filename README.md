#### :book: Описание проекта
---
Foodgram - «Продуктовый помощник» - это онлайн-сервис, где пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.
![Alt text](readme_assets/foodgram_index.jpg)
Это учебный проект, который состоит из бэкенд-приложения на Django и фронтенд-приложения на React. Фронтенд приложение стандартное, и является материалом, предоставленным [Яндекс Практикум](https://practicum.yandex.ru/) вместе с заданием. Бэкенд приложение - это дипломная работа, выполненная в соответствии с предоставленной Яндекс Практикумом спецификацией.


#### :rocket: Запуск проекта на локальном компьютере:
---
- Клонировать репозиторий и перейти в него в командной строке:
```bash
git@github.com:Olkhovik-mv/foodgram-project-react.git
cd foodgram-project-react/
```
- В директории foodgram-project-react/ создать файл `.env` и заполнить его по образцу `.env.example`
- Запустить на компьютере `docker daemon`
- Запустить Docker Compose:
```bash
docker compose up -d
```
- Собрать статику
- Скопировать статику в директорию `/backend_static/`, связанную с volume `static`
- Применить миграции
- Импортировать данные в таблицу `Продукты`
- Создать суперпользователя
```bash
docker compose exec backend python manage.py collectstatic
docker compose exec backend cp -r /app/collected_static/. /backend_static/static/
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py importdata
docker compose exec backend python manage.py createsuperuser
```
- Проект доступен в браузере по адресу: http://localhost:8000
- Зайти в админ-зону проекта http://localhost:8000/admin/ и заполнить таблицу `Теги`.

#### :rocket: Развертывание проекта на удаленном сервере:
---
- Установить на сервер Docker Compose
```bash
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt-get install docker-compose-plugin
```
- Установить Nginx
```bash
sudo apt install nginx -y
```
- Открыть файл конфигурации nginx
```bash
sudo nano /etc/nginx/sites-enabled/default
```
- В файл конфигурации nginx добавить переадресацию на порт 8000
```bash
server {
        listen 80;
        server_name ip_вашего_сервера;

        location / {
                proxy_set_header Host $http_host;
                proxy_pass http://127.0.0.1:8000;       
        }
}
```
- Запустить nginx
```bash
sudo systemctl start nginx
```
- Создать директорию `foodgram`
```bash
cd
mkdir foodgram
```
- Со своего компьютера скопировать файлы `docker-compose.yml` и `.env`в созданную директорию
```bash
scp -i path_to_SSH/SSH_name docker-compose.yml \
  username@server_ip:/home/username/foodgram/docker-compose.yml
scp -i path_to_SSH/SSH_name .env username@server_ip:/home/username/foodgram/.env
```
- Запустить Docker Compose
```bash
sudo docker compose up -d
```
- Собрать статические файлы бэкенда
- Скопировать их в `/backend_static/static/`
- Выполнить миграции
- Импортировать данные в таблицу `Продукты`
- Создать суперпользователя
```bash
sudo docker compose exec backend python manage.py collectstatic
sudo docker compose exec backend cp -r /app/collected_static/. /backend_static/static/
sudo docker compose exec backend python manage.py migrate
sudo docker compose exec backend python manage.py importdata
sudo docker compose exec backend python manage.py createsuperuser
```
- Зайти в админ-зону проекта `http://domen/admin/` и заполнить таблицу `Теги`.
#### :hammer_and_wrench: Технологии:
---
<div>
  <img src="/readme_assets/python-original-wordmark.svg" title="Python" alt="Python" width="40" height="40"/>&nbsp;
  <img src="/readme_assets/react-original-wordmark.svg" title="React" alt="React" width="40" height="40"/>&nbsp;
  <img src="/readme_assets/docker-original-wordmark.svg" title="Docker" alt="Docker" width="40" height="40"/>&nbsp;
  <img src="/readme_assets/django-plain-wordmark.svg" title="Django" alt="Django" width="40" height="40"/>&nbsp;
  <img src="/readme_assets/Django REST.svg" title="Django REST framework" alt="Django REST framework" width="40" height="40"/>&nbsp;
  <img src="/readme_assets/postgresql-original-wordmark.svg" title="PostgreSQL" alt="PostgreSQL" width="40" height="40"/>&nbsp;
  <img src="/readme_assets/github-original-wordmark.svg" title="GitHub" alt="GitHub" width="40" height="40"/>&nbsp;
  <img src="/readme_assets/github-actions.svg" title="GitHub Actions" alt="GitHub Actions" width="40" height="40"/>&nbsp;
  <img src="/readme_assets/git-original-wordmark.svg" title="git" alt="git" width="40" height="40"/>&nbsp;
  <img src="/readme_assets/nginx-original.svg" title="nginx" alt="nginx" width="40" height="40"/>&nbsp;
  <img src="/readme_assets/ssh-original-wordmark.svg" title="ssh" alt="ssh" width="40" height="40"/>&nbsp;
  <img src="/readme_assets/gunicorn.svg" title="gunicorn" alt="gunicorn" width="40" height="40"/>&nbsp;
</div>

#### :man_technologist: Aвторы:
---
- [Яндекс Практикум](https://github.com/yandex-praktikum)
- [Михаил Ольховик](https://github.com/Olkhovik-mv)
---
#### CI/CD status
![workflow](https://github.com/Olkhovik-mv/foodgram-project-react/actions/workflows/main.yml/badge.svg?event=push)

https://cook.ddnsking.com