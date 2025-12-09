
# LearningDjango

Учебный проект на Django + DRF с авторизацией через JWT, оплатами через Stripe и асинхронными задачами на Celery.  
Проект упакован в Docker и использует PostgreSQL и Redis. Настроен автодеплой на VPS через GitHub Actions.

---

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
- **GitHub Actions (CI/CD)**

---

## Основной функционал

- Пользователи (`users`):
  - регистрация, аутентификация (JWT через SimpleJWT, кастомная модель `users.User` с логином по email);
  - управление профилем.
- Материалы (`materials`):
  - курсы и уроки;
  - пагинация, фильтрация, поиск;
  - права доступа и подписки на курсы.
- Платежи (`users.Payment`):
  - оплата курсов и уроков;
  - интеграция со Stripe (Checkout Session, product/price).
- Документация API через **drf-spectacular**:
  - OpenAPI схема, Swagger UI, ReDoc.
- Фоновые задачи Celery (пример: `materials.tasks.test_task`).

---

## 1. Установка и запуск локально через Docker

### 1.1. Клонирование репозитория
```

bash git clone <URL_вашего_репозитория>.git cd LearningDjango```

### 1.2. Подготовка `.env`

В репозитории есть шаблон `.env.sample`. Создайте `.env`:
```

bash cp .env.sample .env``` 

Пример минимального `.env` для локального запуска в Docker:
```

env DEBUG=True SECRET_KEY=ваш_случайный_secret_key
Настройки БД для Django и Postgres
NAME=learningdjango USER=django PASSWORD=your_password HOST=db PORT=5432
Для Celery / Redis
CELERY_BROKER_URL=redis://redis:6379/0 CELERY_RESULT_BACKEND=redis://redis:6379/1
Разрешённые хосты
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
Stripe
STRIPE_API_KEY=sk_test_ваш_ключ STRIPE_SUCCESS_URL=http://localhost:8000/stripe/success/ STRIPE_CANCEL_URL=http://localhost:8000/stripe/cancel/```

Сгенерировать `SECRET_KEY`:
```

bash python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"``` 

### 1.3. Запуск в Docker
```

bash docker compose up --build```

Сервисы:

- `web` — Django + Gunicorn (`http://localhost:8000/`);
- `db` — PostgreSQL;
- `redis` — Redis;
- `worker` — Celery worker;
- `beat` — Celery beat.

Остановить:
```

bash docker compose down``` 

### 1.4. Миграции и суперпользователь

Миграции выполняются автоматически при старте `web`:
```

bash docker compose exec web python manage.py createsuperuser```

---

## 2. Запуск без Docker (через Poetry)

1. Установить Poetry.
2. Установить зависимости:

   ```bash
   poetry install
   ```

3. В `.env` для локального запуска без Docker:

   ```env
   HOST=localhost
   PORT=5432
   ```

   и локально должны быть запущены Postgres и Redis.

4. Запуск:

   ```bash
   poetry run python manage.py migrate
   poetry run python manage.py runserver 0.0.0.0:8000
   ```

Celery локально:
```

bash
worker
poetry run celery -A config worker -l info
beat
poetry run celery -A config beat -l info``` 

---

## 3. Структура проекта
```

text LearningDjango/ ├─ config/ # Настройки Django, urls, wsgi, asgi, celery ├─ materials/ # Приложение с учебными материалами ├─ users/ # Приложение с пользователями и платежами ├─ manage.py ├─ Dockerfile ├─ docker-compose.yml ├─ pyproject.toml ├─ .env.sample └─ README.MD```

---

## 4. API и авторизация

### Основные URL

(по умолчанию в Docker локально и на VPS — порт 8000)

- Админ‑панель:  
  `http://<host>:8000/admin/`

- Материалы:  
  `http://<host>:8000/materials/…`

- Пользователи:  
  `http://<host>:8000/users/…`

### JWT (SimpleJWT)

- Получение токенов:  
  `POST /api/auth/token/`
- Обновление access‑токена:  
  `POST /api/auth/token/refresh/`

Пример запроса:
```

http POST /api/auth/token/ Content-Type: application/json
{ "email": "user@example.com", "password": "password" }``` 

Ответ:
```

json { "access": "…", "refresh": "…" }```

Заголовок для авторизованных запросов:
```

http Authorization: Bearer <access_token>``` 

---

## 5. Документация API

- OpenAPI схема (JSON):  
  `GET /api/schema/`

- Swagger UI:  
  `GET /api/docs/`

- ReDoc:  
  `GET /api/redoc/`

---

## 6. Celery и Redis

В `config/settings.py`:

- `CELERY_BROKER_URL` — URL брокера (Redis),
- `CELERY_RESULT_BACKEND` — backend результатов (Redis).

В `config/celery.py` настроено приложение Celery, автоматически находящее `tasks.py` во всех приложениях.

Пример задачи (`materials/tasks.py`):
```

python from celery import shared_task
@shared_task def test_task(): print("Celery работает!")```

Проверка в Docker:
```

bash docker compose exec web python manage.py shell
from materials.tasks import test_task test_task.delay()``` 

Логи воркера:
```

bash docker compose logs worker```

---

## 7. Развёртывание на VPS по IP

### 7.1. Настройка сервера

На VPS (Ubuntu):
```

bash sudo apt update sudo apt install -y docker.io docker-compose-plugin git sudo systemctl enable docker sudo systemctl start docker sudo usermod -aG docker $USER
затем выйти и зайти снова``` 

Клонировать проект:
```

bash sudo mkdir -p /opt/LearningDjango sudo chown -R USER:USER /opt/LearningDjango cd /opt/LearningDjango git clone <URL_репозитория> .```

Подготовить `.env` (пример для боевого/тестового сервера):
```

env DEBUG=False SECRET_KEY=боевой_secret_key
NAME=learningdjango USER=root PASSWORD=django HOST=db PORT=5432
CELERY_BROKER_URL=redis://redis:6379/0 CELERY_RESULT_BACKEND=redis://redis:6379/1
DJANGO_ALLOWED_HOSTS=<IP_вашего_VPS>,localhost,127.0.0.1
STRIPE_API_KEY=sk_live_или_test STRIPE_SUCCESS_URL=http://<IP_вашего_VPS>:8000/stripe/success/ STRIPE_CANCEL_URL=http://<IP_вашего_VPS>:8000/stripe/cancel/``` 

Запуск:
```

bash cd /opt/LearningDjango docker compose up -d```

Если включён UFW:
```

bash sudo ufw default deny incoming sudo ufw default allow outgoing sudo ufw allow 22/tcp sudo ufw allow 8000/tcp sudo ufw enable sudo ufw status``` 

Теперь приложение доступно по:

- `http://<IP_вашего_VPS>:8000/`
- `http://<IP_вашего_VPS>:8000/admin/`
- `http://<IP_вашего_VPS>:8000/api/docs/`

---

## 8. CI/CD (GitHub Actions)

Workflow находится в `.github/workflows/ci-cd.yml`.

### Триггеры
```

yaml on: push: branches: - develop pull_request: branches: - develop```

### Job `lint-and-test`

- Поднимает сервис Postgres (`services.db`).
- Устанавливает зависимости через Poetry (`poetry install --with lint,dev`).
- Запускает:
    - `black --check .`
    - `isort --check-only .`
    - `ruff check .`
    - `python manage.py test`

При ошибках линтера/тестов деплой не выполняется.

### Job `deploy`
```

yaml deploy: needs: lint-and-test runs-on: ubuntu-latest if: github.ref == 'refs/heads/develop' && github.event_name == 'push'``` 

- Срабатывает **только** при `push` в `develop` (не на PR).
- Подключается по SSH к VPS (используются секреты:
  - `SSH_HOST` — IP сервера,
  - `SSH_USER` — пользователь,
  - `SSH_PORT` — порт SSH,
  - `SSH_PRIVATE_KEY` — приватный ключ для деплоя).
- На сервере:

  ```bash
  APP_DIR=/opt/LearningDjango

  if [ ! -d "$APP_DIR" ]; then
    sudo mkdir -p "$APP_DIR"
    sudo chown -R $USER:$USER "$APP_DIR"
    git clone <URL_репозитория> "$APP_DIR"
  fi

  cd "$APP_DIR"
  git fetch origin
  git reset --hard origin/develop
  docker compose up --build -d
  docker compose exec -T web python manage.py migrate
  ```

Таким образом:

- при коммите в любую ветку `feature/*` можно создать PR в `develop` → будут прогнаны линтеры и тесты (без деплоя);
- при merge/пуше в `develop` выполняется полный деплой на VPS.

---

## 9. Процесс работы с ветками и PR

1. Локально:

   ```bash
   git checkout -b feature/hw-deploy
   # работаешь над задачей
   git push origin feature/hw-deploy
   ```

2. В GitHub создаёшь Pull Request `feature/hw-deploy → develop`.

3. GitHub Actions запускает `lint-and-test` (проверки кода и тесты).

4. Наставник проверяет PR и CI. Если всё ок — мержит в `develop`.

5. При merge (push в `develop`) запускается `deploy`, который обновляет код на VPS и перезапускает Docker‑сервисы.

---

## 10. Полезные команды

bash
# Логи всех сервисов
docker compose logs
# Логи конкретного сервиса
docker compose logs web docker compose logs db docker compose logs worker docker compose logs beat
# Войти в контейнер web
docker compose exec web bash
# Применить миграции
docker compose exec web python manage.py migrate
# Проверить состояние контейнеров
docker compose ps


## Что сделано по критериям ДЗ

1. **Удалённый сервер**
   - VPS на Ubuntu, установлен Docker + docker-compose-plugin.
   - Проект развернут в `/opt/LearningDjango`.
   - Приложение доступно по IP: `http://141.105.71.201:8000/`.
   - UFW: открыт 22 и 8000, остальное закрыто. Доступ по SSH по ключу.

2. **Docker**
   - Написан Dockerfile (Python 3.13 + Poetry + Gunicorn).
   - Настроен `docker-compose.yml` с сервисами: `web`, `db`, `redis`, `worker`, `beat`.

3. **CI/CD (GitHub Actions)**
   - Файл `.github/workflows/ci-cd.yml`.
   - При push/PR в `develop` запускаются линтеры (`black`, `isort`, `ruff`) и тесты.
   - При push в `develop` после успешных тестов выполняется автодеплой на VPS:
     - `git reset --hard origin/develop`,
     - `docker compose up --build -d`,
     - `python manage.py migrate`.

4. **Переменные окружения и Secrets**
   - Шаблон `.env.sample` в репозитории.
   - В CI используются Secrets: `SSH_HOST`, `SSH_USER`, `SSH_PORT`, `SSH_PRIVATE_KEY`.
   - `.env` добавлен в `.gitignore` и не попадает в репозиторий.