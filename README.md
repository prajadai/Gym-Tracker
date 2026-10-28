# Gym Tracker

A lightweight gym tracking application for managing workouts, exercises, training sessions, and progress analytics.

## Tech Stack

- Python 3.13
- FastAPI for the REST API
- Uvicorn for ASGI server
- SQLModel + SQLAlchemy for database models and queries
- SQLite as the default database
- Alembic for database migrations
- Pydantic + pydantic-settings for validation and settings
- JWT authentication with python-jose and bcrypt
- python-multipart for form login requests
- HTML, CSS, and vanilla JavaScript for the frontend
- pytest for automated testing
- uv for Python environment/package management

## Project Requirements

- Python 3.13+
- pip or uv
- A modern browser
- Optional: a .env file for custom configuration

## Dependencies

See the backend requirements:

- fastapi==0.139.2
- uvicorn[standard]==0.51.0
- sqlmodel==0.0.39
- alembic==1.18.5
- pydantic==2.13.4
- pydantic-settings==2.14.2
- python-dotenv==1.2.2
- python-jose[cryptography]==3.5.0
- bcrypt==5.0.0
- python-multipart==0.0.32
- psycopg2-binary==2.9.10

## Setup

1. Clone the repository
   ```bash
   git clone https://github.com/prajadai/Gym-Tracker.git
   cd GymTracker
   ```

2. Create and activate a virtual environment
   ```bash
   cd backend
   python -m venv .venv
   .\.venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment settings (optional)
   Create a `.env` file in the `backend` directory if needed:
   ```env
   DATABASE_URL=sqlite:///./gym.db
   SECRET_KEY=change-me-in-production
   ADMIN_SECRET_KEY=your-admin-key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

5. Run database migrations
   ```bash
   alembic upgrade head
   ```

## Run the Project

### Backend

From the `backend` directory:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

API docs will be available at:
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/redoc

### Frontend

Open the frontend app directly in a browser:

```bash
cd ../frontend
```

Then open `index.html` in your browser or serve the folder locally:

```bash
python -m http.server 5500
```

Then visit: http://127.0.0.1:5500

## Features

- Create and manage exercises
- Track workout sessions
- Add workout sets with reps, weight, and RPE
- View progress analytics
- Authentication and admin access support

## Testing

```bash
cd backend
pytest
```

## Notes

- The app uses SQLite by default for local development.
- The backend is structured as a FastAPI application with modular routers, CRUD logic, and schema validation.
- The frontend is a simple static app that communicates with the FastAPI backend via fetch requests.
