# Events Management System

A robust, glassmorphic events management system built with Python, Django, PostgreSQL, and Docker. 

The system features dynamic event scheduling, interactive timetable timelines, and detailed speaker profile management. It is designed to scale using environment configurations and running dockerized dependencies.

---

## 🛠️ Project Structure

This project isolates settings and configurations from the main feature modules:
*   `core/` - Django configuration, main routing, and basic setup.
    *   `core/settings.py` - Manages Postgres database profiles (inside Docker) with automatic fallback to local SQLite (outside Docker).
    *   `events/` - Feature app containing database schemas, views, templates, and layouts.
*   `Dockerfile` & `docker-compose.yml` - Container configurations.
*   `requirements.txt` - Python package dependencies (including `Pillow` and `psycopg2-binary`).
*   `.env` & `.env.example` - Key-value parameters for environment variables.

---

## 🔑 Environment Variables Setup

Before running the application, make sure to set up your environment configuration.
1. Copy the template `.env.example` file to create a `.env` file at the root:
   ```bash
   cp .env.example .env
   ```
2. Adjust any parameters as needed. The default configuration is optimized to work out-of-the-box for both local development and Docker containers.

---

## 🚀 Getting Started

### Prerequisites
*   [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed on your machine.
*   (Optional for local development) Python 3.12+ installed.

### Method 1: Running with Docker (Recommended)
This method builds the application containers and spins up a dedicated PostgreSQL database container.

1.  **Build and start the services in the background:**
    ```bash
    docker compose up --build -d
    ```
2.  **Access the application:**
    *   Open [http://localhost:8000](http://localhost:8000) in your web browser.
3.  **Run migrations inside the Docker container:**
    ```bash
    docker compose exec web python core/manage.py migrate
    ```
4.  **Create a superuser (Admin panel access):**
    ```bash
    docker compose exec web python core/manage.py createsuperuser
    ```
5.  **Stop the services:**
    ```bash
    docker compose down
    ```

### Method 2: Running Locally (SQLite Fallback)
If you don't have Docker running, the settings automatically fall back to SQLite, making local testing extremely lightweight.

1.  **Create and activate your virtual environment:**
    ```powershell
    python -m venv .venv
    .venv\Scripts\Activate.ps1
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: If you run into build errors compiling `psycopg2-binary` on Windows, you can safely skip it by running `pip install Django Pillow sqlparse tzdata` instead, since SQLite doesn't require psycopg2).*
3.  **Run database migrations:**
    ```bash
    cd core
    python manage.py migrate
    ```
4.  **Create a superuser:**
    ```bash
    python manage.py createsuperuser
    ```
5.  **Start the development server:**
    ```bash
    python manage.py runserver
    ```
    Access the application at [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

---

## 🔗 URL Routing Maps

*   `http://localhost:8000/` - **Home Landing Page** (Hero banner, counter stats, and top 3 featured events).
*   `http://localhost:8000/events/` - **Explore Events** (Grid view of all published events).
*   `http://localhost:8000/events/<id>/` - **Event Timetable** (Chronological schedule of sessions and speakers).
*   `http://localhost:8000/speakers/<id>/` - **Speaker Profile** (Bio, email, social links, and scheduled sessions).
*   `http://localhost:8000/admin/` - **Django Admin panel** (Access interface to manage entries).

---

## 💻 Development Workflow

### Git Branching Strategy
To keep the repository clean and structured:
1.  **`main` Branch**: Contains stable, production-ready core project structures.
2.  **`dev` Branch**: The main integration branch for core configuration changes.
3.  **Feature Branches (`feature/your-feature`)**: All active development (new views, templates, or schemas) must be done on branches off `dev`.
