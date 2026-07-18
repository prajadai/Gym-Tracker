from fastapi import FastAPI
from app.database import create_db_and_tables
from app.routers import exercises, sessions, workout_sets, auth, analytics

app = FastAPI(title="Gym Tracker API", version="0.0.1")


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
def root():
    return {"message": "Welcome to Gym Tracker v0.0.1"}


app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(exercises.router, prefix="/api/v1/exercises", tags=["exercises"])
app.include_router(sessions.router, prefix="/api/v1/sessions", tags=["sessions"])
app.include_router(workout_sets.router, prefix="/api/v1/workout-sets", tags=["workout-sets"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])