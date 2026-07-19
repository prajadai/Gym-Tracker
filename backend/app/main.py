from fastapi import FastAPI
from app.routers import exercises, sessions, workout_sets, auth, analytics
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="Gym Tracker API", version="0.0.1")

@app.get("/")
def root():
    return {"message": "Welcome to Gym Tracker v0.0.1"}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["null", "http://localhost:5500"],  # tighten this to your actual frontend origin once deployed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(exercises.router, prefix="/api/v1/exercises", tags=["exercises"])
app.include_router(sessions.router, prefix="/api/v1/sessions", tags=["sessions"])
app.include_router(workout_sets.router, prefix="/api/v1/workout-sets", tags=["workout-sets"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])