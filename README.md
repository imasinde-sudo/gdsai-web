# Events Management System

A robust events management system built with Python, Django, PostgreSQL, and Docker.

## Project Structure

This project uses a clean architecture separating settings and configuration from functional features.

*   `core/` - Django configuration, routing, and base settings.
*   `Dockerfile` & `docker-compose.yml` - Docker setup for local development.
*   `requirements.txt` - Python package dependencies.

---

## Getting Started

### Prerequisites

*   [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed on your machine.
*   (Optional) Python 3.12+ if running locally outside of Docker.

### Running with Docker (Recommended)

1.  **Build and start the services:**
    ```bash
    docker compose up --build
    ```
    This command will spin up:
    *   `events_db`: PostgreSQL database container.
    *   `events_web`: Django application running on port `8000`.

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

---

## Development Workflow

### Git Branching Strategy

To keep the repository clean and structured:

1.  **`main` Branch**: Contains only stable, production-ready core project structures and fully verified releases.
2.  **`dev` Branch**: The main integration branch for configuration and basic structures.
3.  **Feature Branches (`feature/your-feature`)**: All active development (models, templates, endpoints) must be done on dedicated branches off `dev`.

#### Step-by-Step Feature Workflow

1.  **Checkout to `dev` and pull latest changes:**
    ```bash
    git checkout dev
    git pull
    ```

2.  **Create your feature branch:**
    ```bash
    git checkout -b feature/event-creation
    ```

3.  **Implement your changes and commit locally:**
    ```bash
    git add .
    git commit -m "feat: add event model and migration"
    ```

4.  **Merge changes back to `dev` via Pull Request or manual merge** (after verification).
