// api.js — thin wrapper around fetch() for talking to the FastAPI backend

const API_BASE = "https://gym-tracker-wvu6.onrender.com/api/v1";

const Api = {
  getToken() {
    return localStorage.getItem("iron_log_token");
  },
  setToken(token) {
    localStorage.setItem("iron_log_token", token);
  },
  clearToken() {
    localStorage.removeItem("iron_log_token");
  },

  async request(path, { method = "GET", body = null, auth = true, form = false } = {}) {
    const headers = {};
    if (!form) headers["Content-Type"] = "application/json";
    if (auth) {
      const token = this.getToken();
      if (token) headers["Authorization"] = `Bearer ${token}`;
    }

    const res = await fetch(`${API_BASE}${path}`, {
      method,
      headers,
      body: form ? body : body ? JSON.stringify(body) : null,
    });

    if (res.status === 401) {
      this.clearToken();
      throw new ApiError("Session expired. Please log in again.", 401);
    }

    if (!res.ok) {
      let detail = "Something went wrong.";
      try {
        const data = await res.json();
        detail = data.detail || detail;
      } catch (_) {}
      throw new ApiError(detail, res.status);
    }

    if (res.status === 204) return null;
    return res.json();
  },

  // ---- Auth ----
  register(email, password) {
    return this.request("/auth/register", {
      method: "POST",
      body: { email, password },
      auth: false,
    });
  },

  async login(email, password) {
    const form = new URLSearchParams();
    form.set("username", email);
    form.set("password", password);
    const data = await this.request("/auth/login", {
      method: "POST",
      body: form,
      auth: false,
      form: true,
    });
    this.setToken(data.access_token);
    return data;
  },

  // ---- Exercises ----
  listExercises() {
    return this.request("/exercises/");
  },
  createExercise(name, muscle_group) {
    return this.request("/exercises/", {
      method: "POST",
      body: { name, muscle_group: muscle_group || null },
    });
  },

  // ---- Sessions ----
  listSessions() {
    return this.request("/sessions/");
  },
  createSession(date, notes) {
    return this.request("/sessions/", {
      method: "POST",
      body: { date, notes: notes || null },
    });
  },
  getSession(sessionId) {
    return this.request(`/sessions/${sessionId}`);
  },

  // ---- Workout sets ----
  createSet(sessionId, { exercise_id, set_number, weight, reps, rpe }) {
    return this.request(`/workout-sets/${sessionId}`, {
      method: "POST",
      body: { exercise_id, set_number, weight, reps, rpe: rpe || null },
    });
  },

  // ---- Analytics ----
  getExerciseProgress(exerciseId) {
    return this.request(`/analytics/progress/${exerciseId}`);
  },
};

class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}
