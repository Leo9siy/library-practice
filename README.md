### Library Service Project

An online system to manage library book borrowings, payments via Stripe, and Telegram notifications. 
Built with Django REST Framework, Docker, and Celery.

## Introduction

In many libraries, managing inventory, borrowings, and overdue fines is still a manual process. 
This project solves that by providing a fully functional back-end system that:

Allows users to register, log in, and borrow books.

Automatically calculates payments for borrowings via Stripe.

Sends Telegram notifications on borrowing, return, and overdue cases.

Allows admins to monitor borrowing activity.

No front-end is required — it works via DRF browsable API and Swagger docs.

## How to Start

1. Clone the repository:

git clone https://github.com/Leo9siy/library-practice.git
cd library-practice

2. Set up the environment:

Create a .env file using the provided sample:

cp .env.sample .env

Update the .env values as needed.

3. Build and run using Docker Compose:

docker-compose up --build

This command starts:

Django app (on localhost:8000)

PostgreSQL database

Redis (for Celery)

Celery worker

Celery Beat (for periodic tasks)

4. Apply migrations and create a superuser:

docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser

5. Access the app:

API: http://localhost:8000/api/

Swagger docs: http://localhost:8000/api/schema/swagger-ui/

Admin: http://localhost:8000/admin/

✅ Features

💰 Stripe Payments (Borrowing & Fines)

🔔 Telegram Notifications

🗓 Overdue Check via Celery Beat

🧪 Testing

To run tests:

docker-compose exec web python manage.py test

Test coverage: 60%+ required.

⚙️ Tech Stack

Python 3.13

Django + DRF

PostgreSQL

Redis + Celery + Celery Beat

Stripe

Docker + Docker Compose