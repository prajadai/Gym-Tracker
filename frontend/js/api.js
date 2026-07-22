// api.js — thin wrapper around fetch() for talking to the FastAPI backend

// const API_BASE = "https://gym-tracker-wvu6.onrender.com/api/v1";
const isLocal = ["localhost", "127.0.0.1", ""].includes(window.location.hostname);
const API_BASE = isLocal
  ? "http://127.0.0.1:8000/api/v1"
  : "https://gym-tracker-wvu6.onrender.com/api/v1";

const Api = {
  // Set by app.js at boot — called any time we detect the session is
  // gone (expired locally, or the server rejected the token with 401).
  onSessionExpired: null,

  getToken() {
    return localStorage.getItem("iron_log_token");
  },
  setToken(token) {
    localStorage.setItem("iron_log_token", token);
    this._scheduleExpiryLogout(token);
  },
  clearToken() {
    localStorage.removeItem("iron_log_token");
    clearTimeout(this._expiryTimer);
  },

  // Decodes the JWT payload without verifying the signature (we don't
  // need to — the server verifies it; this is purely so the UI can react
  // to expiry without waiting on a failed network request).
  _decodeJwt(token) {
    try {
      const payload = token.split(".")[1];
      const json = atob(payload.replace(/-/g, "+").replace(/_/g, "/"));
      return JSON.parse(json);
    } catch (_) {
      return null;
    }
  },

  // Returns true only if we have a token AND its exp claim is in the future.
  isTokenValid() {
    const token = this.getToken();
    if (!token) return false;
    const payload = this._decodeJwt(token);
    if (!payload || !payload.exp) return false;
    return payload.exp * 1000 > Date.now();
  },

  // Schedules an automatic logout for the exact moment the current token
  // expires, so a session doesn't just silently die mid-use — the user
  // gets bounced to the login screen the instant it happens.
  _scheduleExpiryLogout(token) {
    clearTimeout(this._expiryTimer);
    const payload = this._decodeJwt(token);
    if (!payload || !payload.exp) return;
    const msUntilExpiry = payload.exp * 1000 - Date.now();
    if (msUntilExpiry <= 0) return;
    this._expiryTimer = setTimeout(() => {
      this.clearToken();
      if (this.onSessionExpired) this.onSessionExpired();
    }, msUntilExpiry);
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
      if (auth && this.onSessionExpired) this.onSessionExpired();
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
