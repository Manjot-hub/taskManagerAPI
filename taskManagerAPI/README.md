# TaskFlow API

A production-ready REST API for task management built with Django REST Framework. Designed with system design principles in mind — caching, async task processing, security, and scalability.

---

## Tech Stack

- **Backend** — Django 6.0, Django REST Framework
- **Database** — PostgreSQL
- **Cache & Message Broker** — Redis
- **Background Tasks** — Celery + Celery Beat
- **Authentication** — JWT (djangorestframework-simplejwt)
- **API Docs** — Swagger UI (drf-spectacular)

---

## High Level Architecture

```
                     ┌─────────────────┐
                     │   Client        │
                     │ (Browser/App)   │
                     └────────┬────────┘
                              │ HTTP requests
                              ▼
                     ┌─────────────────┐
                     │   Django        │
                     │   Web Server    │
                     │   (Port 8000)   │
                     └────────┬────────┘
                              │
             ┌────────────────┼────────────────┐
             ▼                ▼                ▼
     ┌──────────┐    ┌──────────────┐   ┌──────────┐
     │  Auth    │    │  Tasks API   │   │  Swagger │
     │ /token/  │    │  /api/v1/    │   │  /docs/  │
     └──────────┘    └──────┬───────┘   └──────────┘
                            │
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
     ┌──────────┐   ┌──────────────┐  ┌──────────┐
     │  Redis   │   │  PostgreSQL  │  │  Celery  │
     │  Cache   │   │  Database    │  │  Worker  │
     └──────────┘   └──────────────┘  └────┬─────┘
                                           │
                                    ┌──────▼─────┐
                                    │   Gmail    │
                                    │   SMTP     │
                                    └────────────┘
```

---

## Features

- User registration and JWT authentication
- Full CRUD for tasks with user isolation
- Custom permissions — users can only access their own tasks
- Filtering by status and priority
- Search by title and description
- Ordering by created date, due date, priority
- Pagination
- Forgot password with email reset flow
- Redis caching — cache-aside pattern on task list
- Celery async email sending
- Celery Beat — scheduled due date reminders daily at 8AM
- Rate limiting and throttling
- Custom error handling — consistent error responses
- API versioning — `/api/v1/`
- Swagger docs — `/api/v1/docs/`
- Separate settings for dev and prod environments
- Database indexes on frequently queried fields

---

## API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/register/` | Register a new user | No |
| POST | `/api/v1/token/` | Login and get JWT tokens | No |
| POST | `/api/v1/token/refresh/` | Refresh access token | No |
| POST | `/api/v1/password-reset/` | Request password reset email | No |
| POST | `/api/v1/password-reset/confirm/` | Confirm password reset | No |
| GET | `/api/v1/tasks/` | List all tasks (paginated) | Yes |
| POST | `/api/v1/tasks/` | Create a new task | Yes |
| GET | `/api/v1/tasks/<id>/` | Get a specific task | Yes |
| PUT | `/api/v1/tasks/<id>/` | Update a task | Yes |
| PATCH | `/api/v1/tasks/<id>/` | Partial update a task | Yes |
| DELETE | `/api/v1/tasks/<id>/` | Delete a task | Yes |
| GET | `/api/v1/docs/` | Swagger API documentation | No |

### Query Parameters for `GET /api/v1/tasks/`

| Parameter | Description | Example |
|-----------|-------------|---------|
| `status` | Filter by status | `?status=pending` |
| `priority` | Filter by priority | `?priority=high` |
| `search` | Search title/description | `?search=meeting` |
| `ordering` | Order results | `?ordering=-created_at` |
| `page` | Page number | `?page=2` |

---

## Request & Response Examples

### Register
```json
POST /api/v1/register/
{
    "username": "john",
    "email": "john@example.com",
    "password": "securepass123"
}
```

### Login
```json
POST /api/v1/token/
{
    "username": "john",
    "password": "securepass123"
}

Response:
{
    "access": "eyJhbGci...",
    "refresh": "eyJhbGci..."
}
```

### Create Task
```json
POST /api/v1/tasks/
Authorization: Bearer <access_token>
{
    "title": "Finish project report",
    "description": "Include Q4 metrics",
    "status": "pending",
    "priority": "high",
    "due_date": "2026-03-10"
}
```

---

## Project Structure

```
taskManagerAPI/                  # outer project root
├── taskManagerAPI/              # Django project folder
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py             # shared settings
│   │   ├── dev.py              # development settings
│   │   └── prod.py             # production settings
│   ├── __init__.py
│   ├── asgi.py
│   ├── celery.py               # Celery configuration
│   ├── urls.py                 # root URL configuration
│   └── wsgi.py
├── tasks/                      # main app
│   ├── migrations/
│   │   ├── __init__.py
│   │   ├── 0001_initial.py
│   │   ├── 0002_alter_task_options.py
│   │   └── 0003_task_tasks_task_o.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py               # Task model with indexes
│   ├── permissions.py          # IsOwner custom permission
│   ├── serializers.py          # Task, Register, PasswordReset serializers
│   ├── task_jobs.py            # Celery background tasks
│   ├── tests.py                # API tests
│   ├── urls.py                 # app URL routing
│   ├── utils.py                # custom exception handler
│   └── views.py                # ViewSets and API views
├── templates/
│   └── index.html              # Frontend
├── .env.example
├── .gitignore
├── manage.py
└── requirements.txt
```

---

## Local Setup

### Prerequisites

- Python 3.13+
- PostgreSQL
- Redis

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/taskManagerAPI.git
cd taskManagerAPI
```

### 2. Create and activate virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

```env
SECRET_KEY=your-secret-key-here
DEBUG=True

DB_NAME=taskmanager
DB_USER=taskmanager_user
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432

REDIS_URL=redis://127.0.0.1:6379/1

EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_gmail@gmail.com
EMAIL_HOST_PASSWORD=your_gmail_app_password
```

### 5. Set up PostgreSQL

```sql
CREATE DATABASE taskmanager;
CREATE USER taskmanager_user WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE taskmanager TO taskmanager_user;
GRANT ALL ON SCHEMA public TO taskmanager_user;
ALTER DATABASE taskmanager OWNER TO taskmanager_user;
ALTER USER taskmanager_user CREATEDB;
```

### 6. Run migrations

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 7. Start Redis

Make sure Redis is running on port 6379.

```bash
# Windows (if installed as service, it runs automatically)
redis-cli ping  # should return PONG
```

### 8. Start the Django server

```bash
python manage.py runserver
```

### 9. Start Celery worker (new terminal)

```bash
celery -A taskManagerAPI worker --loglevel=info --pool=solo
```

### 10. Start Celery Beat (new terminal)

```bash
celery -A taskManagerAPI beat --loglevel=info
```

Visit `http://127.0.0.1:8000` for the frontend and `http://127.0.0.1:8000/api/v1/docs/` for API documentation.

---

## Running Tests

```bash
python manage.py test tasks
```

---

## System Design Decisions

**PostgreSQL over SQLite**
ACID compliant, handles concurrent writes, supports proper indexing. SQLite is not suitable for production workloads.

**Redis for caching**
In-memory store with microsecond reads. Task list responses are cached for 5 minutes using the cache-aside pattern. Cache is invalidated on any write operation.

**Celery for async tasks**
Decouples slow operations like email sending from the request/response cycle. API returns immediately while Celery handles the work in the background.

**JWT over sessions**
Stateless authentication — no server-side session storage needed. Scales horizontally without sticky sessions.

**Database indexes**
Indexes on `owner`, `status`, `priority`, `due_date`, and composite `(owner, status)` prevent full table scans on large datasets.

**Rate limiting**
Login and register endpoints are limited to 5 requests per minute. Authenticated users are limited to 200 requests per hour.

**Separate settings**
`base.py` contains shared config. `dev.py` and `prod.py` override what's needed per environment. Production enforces HTTPS, strict CORS, and security headers.

---

## Environment Variables Reference

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | Debug mode (True/False) |
| `DB_NAME` | PostgreSQL database name |
| `DB_USER` | PostgreSQL username |
| `DB_PASSWORD` | PostgreSQL password |
| `DB_HOST` | PostgreSQL host |
| `DB_PORT` | PostgreSQL port |
| `REDIS_URL` | Redis connection URL |
| `EMAIL_HOST_USER` | Gmail address |
| `EMAIL_HOST_PASSWORD` | Gmail app password |

---

## License

MIT
