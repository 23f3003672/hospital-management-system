![Python](https://img.shields.io/badge/Python-3.x-blue)
![Flask](https://img.shields.io/badge/Flask-Backend-black)
![Vue.js](https://img.shields.io/badge/Vue.js-Frontend-42b883)
![Redis](https://img.shields.io/badge/Redis-Cache-red)
![Celery](https://img.shields.io/badge/Celery-Background%20Tasks-green)
# 🏥 Hospital Management System

The application streamlines hospital operations by providing separate interfaces for **Administrators**, **Doctors**, and **Patients**, enabling efficient management of appointments, treatments, medical records, and user workflows.

This project demonstrates the development of a modern web application using a REST API backend, Vue.js frontend, Redis caching, and Celery background task processing.

---

## Features

### Administrator
- Manage doctors and patients
- Schedule and manage appointments
- Monitor hospital records
- Manage system users

### Doctor
- View assigned appointments
- Access patient medical records
- Update diagnoses and treatment details
- Manage consultation history

### Patient
- Register and log in securely
- Book appointments
- View appointment history
- Access treatment and medical records

---

## Tech Stack

### Backend
- Flask (REST APIs)
- SQLite
- SQLAlchemy
- Flask-Security (Authentication & Authorization)
- Redis (Caching)
- Celery + Redis (Background Tasks)
- Flask-Mail (Email Services)
- MailHog (Local Email Testing)

### Frontend
- Vue.js (Options API)
- Vue Router
- Bootstrap

---

## Project Highlights

- Full-stack web application
- RESTful API architecture
- Role-based authentication and authorization
- Appointment management workflow
- Medical record management
- Redis-based caching
- Asynchronous background jobs using Celery
- Email notification support
- Responsive web interface

---

## Project Structure

```
Hospital-Management-System/
│
├── backend/
│   ├── APIs
│   ├── Models
│   ├── Tasks
│   ├── Config
│   └── ...
│
├── frontend/
│   ├── components/
│   ├── views/
│   ├── router/
│   └── ...
│
├── README.md
└── requirements.txt
```

---

## Installation

### Clone the repository

```bash
git clone https://github.com/23f3003672/hospital-management-system.git
cd Hospital-Management-System
```

### Install backend dependencies

```bash
pip install -r requirements.txt
```

### Install frontend dependencies

```bash
npm install
```

---

## Running the Application

### Start Redis

```bash
redis-server
```

### Start Celery Worker

```bash
celery -A app.celery worker --loglevel=info
```

### Start Flask Backend

```bash
python app.py
```

### Start Vue Frontend

```bash
npm run serve
```

---

## Learning Outcomes

This project demonstrates practical implementation of:

- REST API development using Flask
- Full-stack application architecture
- Authentication and role-based access control
- Database design using SQLAlchemy
- Redis caching
- Background task processing with Celery
- Vue.js frontend development
- Client-server communication
- Responsive UI development

