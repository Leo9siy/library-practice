### Library Service Project

An online system to manage library book borrowings, payments via Stripe, and Telegram notifications. 
Built with Django REST Framework, Docker, and Celery.

## Introduction

This is a backend API project that allows:
- Users to borrow books
- Manage returns and fees
- Stripe integration for secure online payments
- Celery with Redis for background tasks (e.g., cleaning expired sessions)
- Admin access for data monitoring

Technologies used:
- Django / DRF
- PostgreSQL
- Stripe API
- Celery + Redis
- Docker / Docker Compose

## How to Start

1. Clone the repository:

git clone https://github.com/Leo9siy/library-practice.git
cd library-practice

2. Set up the environment:

Create a .env file using the provided sample:
cp .env.sample .env
Update the .env values as needed.

3. Start the Project

docker-compose up --build

This command starts:

- Django app (on localhost:8000)
- PostgreSQL database
- Redis (for Celery)
- Celery worker
- Celery Beat (for periodic tasks)

4. Apply migrations and create a superuser:
`docker-compose exec web python manage.py migrate`

5. Create Superuser (optional)
`docker-compose exec web python manage.py createsuperuser`

## API Overview

- Base URL (local): http://localhost:8000/api/

# Endpoints

- /books/ – list & detail of books
- /borrowings/ – create & return borrowings
- /payments/ – view payment sessions

Auth

- JWT authentication (login, refresh)


# Run Tests

`docker-compose exec web python manage.py test`

# Periodic Tasks (Celery Beat)

Check expired Stripe sessions — expire_old_payments runs every 30 minutes
