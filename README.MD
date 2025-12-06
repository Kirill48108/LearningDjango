
# LearningDjango

Учебный проект на Django + DRF с авторизацией через JWT, оплатами через Stripe и асинхронными задачами на Celery.  
Проект упакован в Docker и использует PostgreSQL и Redis.



## Стек

- **Python** 3.13
- **Django** 5.2
- **Django REST Framework**
- **PostgreSQL**
- **Redis**
- **Celery** (worker + beat)
- **Stripe**
- **Gunicorn**
- **Docker / Docker Compose**



## Основной функционал

Кратко, что делает приложение (заполни по своему ТЗ, здесь пример):

- Регистрация и аутентификация пользователей (кастомная модель `users.User`).
- Работа с учебными материалами (`materials`):
  - список и детальный просмотр;
  - фильтрация и поиск;
  - права доступа.
- Оплата доступа к материалам через Stripe:
  - создание сессий Checkout;
  - обработка успешной/отменённой оплаты.
- Документация API через **drf-spectacular** (OpenAPI/Swagger).
- Асинхронные фоновые задачи на Celery.



## Установка и запуск

### 1. Клонирование репозитория


bash git clone <URL_вашего_репозитория>.git cd LearningDjango```

### 2. Подготовка `.env`

В репозитории есть шаблон `.env.sample`.  
Создайте на его основе рабочий `.env`:


bash cp .env.sample .env

Заполните переменные окружения. Пример (минимально необходимый):


env DEBUG=True SECRET_KEY=ваш_случайный_secret_key
Настройки БД для Django (config/settings.py)
NAME=learningdjango USER=django PASSWORD=your_password HOST=db PORT=5432
Для Celery / Redis
CELERY_BROKER_URL=redis://redis:6379/0 CELERY_RESULT_BACKEND=redis://redis:6379/1
(опционально) список разрешённых хостов
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
Stripe
STRIPE_API_KEY=sk_test_ваш_ключ STRIPE_SUCCESS_URL=http://localhost:8000/stripe/success/ STRIPE_CANCEL_URL=http://localhost:8000/stripe/cancel/```

> `SECRET_KEY` можно сгенерировать так:
> bash
> python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"


### 3. Запуск в Docker

Убедитесь, что Docker и Docker Compose установлены и запущен docker‑daemon.

Собрать и поднять все сервисы:


bash docker compose up --build``` 

Будут запущены:

- `web` — Django + Gunicorn (`http://localhost:8000/`)
- `db` — PostgreSQL
- `redis` — Redis
- `worker` — Celery worker
- `beat` — Celery beat

Остановить контейнеры:


bash docker compose down```

#### Миграции и суперпользователь

Миграции выполняются автоматически при старте `web` (в команде контейнера).

Создать суперпользователя:


bash docker compose exec web python manage.py createsuperuser``` 



## Запуск без Docker (локально, через Poetry)

1. Установите Poetry.
2. Установите зависимости:

   bash
   poetry install
   

3. Создайте и заполните `.env` (как выше), но в этом случае:
    - `HOST=localhost`
    - PostgreSQL и Redis должны быть установлены и запущены локально.

4. Запуск сервера:

   bash
   poetry run python manage.py migrate
   poetry run python manage.py runserver
   

Celery локально:


bash
worker
poetry run celery -A config worker -l info
beat
poetry run celery -A config beat -l info``` 



## Структура проекта


text LearningDjango/ ├─ config/ # Настройки Django, urls, wsgi, celery ├─ materials/ # Приложение с учебными материалами ├─ users/ # Приложение с пользователями (кастомная модель User) ├─ manage.py ├─ Dockerfile ├─ docker-compose.yml ├─ pyproject.toml ├─ .env.sample └─ README.MD```



## API и авторизация

### Основные URL

- Админ‑панель:  
  `http://localhost:8000/admin/`

- Материалы (точные пути — в `materials/urls.py`):  
  `http://localhost:8000/materials/…`

- Пользователи (точные пути — в `users/urls.py`):  
  `http://localhost:8000/users/…`

### JWT‑аутентификация (SimpleJWT)

- Получение пары токенов (access + refresh):  
  `POST /api/auth/token/`

- Обновление access‑токена по refresh:  
  `POST /api/auth/token/refresh/`

Пример запроса на получение токена:


http POST /api/auth/token/ Content-Type: application/json
{ "email": "user@example.com", "password": "password" }``` 

(Если используется логин по username — укажи нужное поле вместо `email`.)

В ответ придёт:


json { "access": "…", "refresh": "…" }```

Дальше во всех защищённых эндпоинтах передаём:


http Authorization: Bearer``` 

-

## Документация API

Проект использует **drf-spectacular**. Доступные эндпоинты документации:

- JSON‑схема OpenAPI:  
  `GET /api/schema/`

- Swagger UI:  
  `GET /api/docs/`

- ReDoc:  
  `GET /api/redoc/`



## Celery и Redis

В `config/settings.py` используются переменные окружения:

- `CELERY_BROKER_URL` — URL брокера сообщений (Redis).
- `CELERY_RESULT_BACKEND` — backend для хранения результатов.

В `config/celery.py` настроено Celery‑приложение, которое автоматически находит `tasks.py` во всех Django‑приложениях.

Пример проверки работоспособности Celery:


bash docker compose exec web python manage.py shell
from materials.tasks import example_task example_task.delay()```

Логи воркера:


bash docker compose logs worker``` 



## Stripe

Для работы Stripe нужны переменные окружения:

- `STRIPE_API_KEY` — секретный ключ (в личном кабинете Stripe:  
  **Developers → API keys → Secret key** — тестовый ключ вида `sk_test_...`).
- `STRIPE_SUCCESS_URL` — URL, куда пользователь попадёт после успешной оплаты.
- `STRIPE_CANCEL_URL` — URL, куда попадёт при отмене оплаты.

Пример конфигурации в `.env`:


env STRIPE_API_KEY=sk_test_... STRIPE_SUCCESS_URL=http://localhost:8000/stripe/success/ STRIPE_CANCEL_URL=http://localhost:8000/stripe/cancel/```

---

## Тесты и покрытие

(Если у тебя уже есть тесты — опиши здесь, как их запускать. Пример:)


bash
В Docker
docker compose exec web coverage run manage.py test docker compose exec web coverage html``` 

Или локально через Poetry:


bash poetry run coverage run manage.py test poetry run coverage html```



## Полезные команды


bash
Логи всех сервисов
docker compose logs
Логи конкретного сервиса
docker compose logs web docker compose logs db docker compose logs worker docker compose logs beat
Войти в контейнер web
docker compose exec web bash``` 

