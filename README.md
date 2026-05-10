# Employee Management System

Django-based employee management system with dynamic form builder and REST API.

## Setup

```bash
git clone <repo-url>
cd employee_management_system_django
conda create -n emp_man_sys python=3.10
conda activate emp_man_sys
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Features
- Auth: Register, Login, Profile, Change Password
- Dynamic form builder with custom fields
- Employee CRUD
- REST APIs with JWT authentication

## API Endpoints
- `POST /accounts/api/register/`
- `POST /accounts/api/login/`
- `GET/PUT /accounts/api/profile/`
- `POST /accounts/api/change-password/`
- `GET/POST /api/forms/`
- `GET/PUT/DELETE /api/forms/<id>/`
- `GET/POST /api/employees/`
- `GET/PUT/DELETE /api/employees/<id>/`

## Postman
Import `postman_collection.json` and run **Login** first.