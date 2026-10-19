# Habit Tracker

Веб-приложение для отслеживания привычек на Django + Celery + Redis + PostgreSQL. Разворачивается в Docker за Nginx.

**SERVER_IP:** `85.208.86.252`  
**Сайт:** http://85.208.86.252

---

## Стек

- Python 3.14, Django 4.x, Gunicorn 26.2
- PostgreSQL 16, Redis 7, Celery 5
- Nginx 1.27, Docker Compose v2

---

## Быстрый старт (локально)

```bash
git clone git@github.com:dementievaolga082489/Habit_Tracker.git
cd Habit_Tracker
cp .env.example .env
docker compose up -d --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser