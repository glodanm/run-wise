# RunWise Backend API

RunWise is an AI-powered running coach application. This repository contains the backend API built with **FastAPI**, designed using **Clean Architecture** principles and **Dependency Injection**.

## Tech Stack

The project uses modern Python tools and libraries:

* **Core Framework**: [FastAPI](https://fastapi.tiangolo.com/)
* **Database**: PostgreSQL with [SQLAlchemy (Async)](https://www.sqlalchemy.org/)
* **Migrations**: [Alembic](https://alembic.sqlalchemy.org/)
* **Dependency Injection**: [`dependency-injector`](https://python-dependency-injector.ets-labs.org/) framework for wiring components.
* **Package Manager**: [uv](https://github.com/astral-sh/uv) (blazing fast Python package installer).
* **Containerization**: Docker & Docker Compose.

## Prerequisites

Before you begin, ensure you have the following installed:
* **Docker** & **Docker Compose**
* **Python 3.12+** (optional, for local debugging)
* **uv** (optional, for local debugging)

## How to Run (Getting Started)

### 1. Environment Setup

Create a `.env` file based on the example and fill in your credentials (DB, Strava keys):

```bash
cp .env.example .env

```

### 2. Start the Application

Build and start the containers using Docker Compose:

```bash
docker-compose up --build

```

The API will be available at: [http://localhost:8000](https://www.google.com/search?q=http://localhost:8000)

### 3. Database Migrations

Since the app is running in Docker, you should run migration commands **inside the container**.

**Apply Migrations (Upgrade DB):**

```bash
docker compose exec run-wise-app-1 uv run alembic upgrade head

```

**Create a New Migration (after changing models):**

```bash
docker compose exec run-wise-app-1 uv run alembic revision --autogenerate -m "describe_your_changes"

```

*Note: `app` is the service name defined in `docker-compose.yml`.*

## Development Guide

### Project Structure

The project follows a modular structure:

* `src/core/`: Global configuration, Database connection, DI Container.
* `src/domain/`: Pure business entities.
* `src/modules/`: Feature-based modules (e.g., `authorization`).

### Dependency Injection Workflow

We use `dependency-injector` to manage dependencies.

1. **Define Components:** Create Repository and Service classes.
2. **Register:** Add them to `src/core/container.py`.
3. **Inject:** Use factory injection in `dependencies.py` and `Depends()` in routers.

### Strava Integration

The project includes a `StravaService` for OAuth2 authentication.
Make sure your `.env` has valid `STRAVA_CLIENT_ID` and `STRAVA_CLIENT_SECRET`.
