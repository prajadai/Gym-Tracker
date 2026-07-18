// app.js — UI logic for Iron Log

const el = (id) => document.getElementById(id);
let currentSessionId = null;
let exercisesCache = [];

// ---------------- Toast ----------------
function showToast(message, isError = false) {
  const toast = el("toast");
  toast.textContent = message;
  toast.classList.toggle("error", isError);
  toast.classList.remove("hidden");
  clearTimeout(showToast._t);
  showToast._t = setTimeout(() => toast.classList.add("hidden"), 3000);
}

// ---------------- View switching ----------------
function showAuthView() {
  el("auth-view").classList.remove("hidden");
  el("app-view").classList.add("hidden");
}

function showAppView() {
  el("auth-view").classList.add("hidden");
  el("app-view").classList.remove("hidden");
  showPanel("sessions-panel");
  loadSessions();
}

function showPanel(panelId) {
  document.querySelectorAll(".panel").forEach((p) => p.classList.add("hidden"));
  el(panelId).classList.remove("hidden");
  document.querySelectorAll(".nav-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.view === panelId);
  });
}

// ---------------- Auth tabs ----------------
document.querySelectorAll(".tab-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    const isLogin = btn.dataset.tab === "login";
    el("login-form").classList.toggle("hidden", !isLogin);
    el("register-form").classList.toggle("hidden", isLogin);
  });
});

el("login-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  el("login-error").textContent = "";
  try {
    await Api.login(el("login-email").value, el("login-password").value);
    showAppView();
  } catch (err) {
    el("login-error").textContent = err.message;
  }
});

el("register-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  el("register-error").textContent = "";
  try {
    await Api.register(el("register-email").value, el("register-password").value);
    await Api.login(el("register-email").value, el("register-password").value);
    showAppView();
  } catch (err) {
    el("register-error").textContent = err.message;
  }
});

el("logout-btn").addEventListener("click", () => {
  Api.clearToken();
  showAuthView();
});

// ---------------- Top nav ----------------
document.querySelectorAll(".nav-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    showPanel(btn.dataset.view);
    if (btn.dataset.view === "progress-panel") loadProgressPanel();
  });
});

// ---------------- Sessions list ----------------
async function loadSessions() {
  const list = el("sessions-list");
  list.innerHTML = "<p class='empty-state'>Loading…</p>";
  try {
    const sessions = await Api.listSessions();
    if (!sessions.length) {
      list.innerHTML = "<div class='empty-state'>No sessions yet. Log your first workout to get started.</div>";
      return;
    }
    // Most recent first
    sessions.sort((a, b) => new Date(b.date) - new Date(a.date));
    list.innerHTML = "";
    sessions.forEach((s) => {
      const card = document.createElement("div");
      card.className = "session-card";
      card.innerHTML = `
        <div>
          <div class="session-card-date">${formatDate(s.date)}</div>
          ${s.notes ? `<div class="session-card-notes">${escapeHtml(s.notes)}</div>` : ""}
        </div>
      `;
      card.addEventListener("click", () => openSessionDetail(s.id));
      list.appendChild(card);
    });
  } catch (err) {
    showToast(err.message, true);
  }
}

function formatDate(dateStr) {
  const d = new Date(dateStr + "T00:00:00");
  return d.toLocaleDateString(undefined, { weekday: "short", month: "short", day: "numeric", year: "numeric" });
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

// ---------------- New session modal ----------------
el("new-session-btn").addEventListener("click", () => {
  el("session-date").value = new Date().toISOString().slice(0, 10);
  el("new-session-modal").classList.remove("hidden");
});

document.querySelectorAll("[data-close-modal]").forEach((btn) =>
  btn.addEventListener("click", () => el("new-session-modal").classList.add("hidden"))
);

el("new-session-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    const session = await Api.createSession(el("session-date").value, el("session-notes").value);
    el("new-session-modal").classList.add("hidden");
    el("new-session-form").reset();
    showToast("Session created");
    await loadSessions();
    openSessionDetail(session.id);
  } catch (err) {
    showToast(err.message, true);
  }
});

// ---------------- Session detail ----------------
async function openSessionDetail(sessionId) {
  currentSessionId = sessionId;
  showPanel("session-detail-panel");
  await renderSessionDetail();
  await populateExerciseDropdown();
}

el("back-to-sessions").addEventListener("click", () => {
  showPanel("sessions-panel");
  loadSessions();
});

async function renderSessionDetail() {
  const container = el("session-detail-content");
  container.innerHTML = "<p class='empty-state'>Loading…</p>";
  try {
    const s = await Api.getSession(currentSessionId);
    let html = `
      <div class="session-detail-header">
        <div class="session-detail-date">${formatDate(s.date)}</div>
        ${s.notes ? `<div class="session-card-notes">${escapeHtml(s.notes)}</div>` : ""}
        <div class="session-summary-stats">
          <div class="stat-block">
            <div class="stat-value">${s.total_exercises}</div>
            <div class="stat-label">Exercises</div>
          </div>
          <div class="stat-block">
            <div class="stat-value">${s.total_sets}</div>
            <div class="stat-label">Sets</div>
          </div>
        </div>
      </div>
    `;

    if (!s.exercises.length) {
      html += "<div class='empty-state'>No sets logged yet. Add one below.</div>";
    } else {
      s.exercises.forEach((group) => {
        const maxWeight = Math.max(...group.sets.map((set) => set.weight));
        html += `<div class="exercise-group">
          <div class="exercise-group-name">${escapeHtml(group.exercise_name)}</div>`;
        group.sets.forEach((set) => {
          const isTop = set.weight === maxWeight;
          html += `<div class="set-row">
            <span>Set ${set.set_number}</span>
            <span class="weight-stamp ${isTop ? "is-pr" : ""}">${set.weight}kg</span>
            <span>× ${set.reps} reps</span>
            ${set.rpe ? `<span>RPE ${set.rpe}</span>` : ""}
          </div>`;
        });
        html += `</div>`;
      });
    }

    container.innerHTML = html;
  } catch (err) {
    showToast(err.message, true);
  }
}

// ---------------- Exercise dropdown + quick add ----------------
async function populateExerciseDropdown() {
  try {
    exercisesCache = await Api.listExercises();
    const select = el("set-exercise");
    select.innerHTML = exercisesCache
      .map((ex) => `<option value="${ex.id}">${escapeHtml(ex.name)}</option>`)
      .join("");
  } catch (err) {
    showToast(err.message, true);
  }
}

el("new-exercise-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    await Api.createExercise(el("exercise-name").value, el("exercise-muscle-group").value);
    el("new-exercise-form").reset();
    showToast("Exercise added");
    await populateExerciseDropdown();
  } catch (err) {
    showToast(err.message, true);
  }
});

// ---------------- Add set ----------------
el("add-set-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    await Api.createSet(currentSessionId, {
      exercise_id: parseInt(el("set-exercise").value, 10),
      set_number: parseInt(el("set-number").value, 10),
      weight: parseFloat(el("set-weight").value),
      reps: parseInt(el("set-reps").value, 10),
      rpe: el("set-rpe").value ? parseFloat(el("set-rpe").value) : null,
    });
    showToast("Set logged");
    el("set-number").value = parseInt(el("set-number").value, 10) + 1;
    el("set-weight").value = "";
    el("set-reps").value = "";
    el("set-rpe").value = "";
    await renderSessionDetail();
  } catch (err) {
    showToast(err.message, true);
  }
});

// ---------------- Progress panel ----------------
async function loadProgressPanel() {
  const select = el("progress-exercise-select");
  try {
    if (!exercisesCache.length) exercisesCache = await Api.listExercises();
    select.innerHTML = exercisesCache
      .map((ex) => `<option value="${ex.id}">${escapeHtml(ex.name)}</option>`)
      .join("");
    if (exercisesCache.length) {
      await renderProgress(exercisesCache[0].id);
    } else {
      el("progress-content").innerHTML = "<div class='empty-state'>Add an exercise first to see progress.</div>";
    }
  } catch (err) {
    showToast(err.message, true);
  }
}

el("progress-exercise-select").addEventListener("change", (e) => {
  renderProgress(parseInt(e.target.value, 10));
});

async function renderProgress(exerciseId) {
  const container = el("progress-content");
  container.innerHTML = "<p class='empty-state'>Loading…</p>";
  try {
    const data = await Api.getExerciseProgress(exerciseId);
    if (!data.history.length) {
      container.innerHTML = "<div class='empty-state'>No sets logged for this exercise yet.</div>";
      return;
    }
    let html = `
      <div class="progress-summary">
        <div class="pb-block">
          <div class="pb-value">${data.personal_best_weight}kg</div>
          <div class="pb-label">Personal best</div>
        </div>
      </div>
      <div class="progress-history">
    `;
    [...data.history].reverse().forEach((point) => {
      html += `<div class="progress-row">
        <span class="row-date">${formatDate(point.date)}</span>
        <span class="row-max">${point.max_weight}kg</span>
        <span>${point.total_sets} sets</span>
        <span>${point.total_volume}kg vol</span>
      </div>`;
    });
    html += `</div>`;
    container.innerHTML = html;
  } catch (err) {
    showToast(err.message, true);
  }
}

// ---------------- Boot ----------------
if (Api.getToken()) {
  showAppView();
} else {
  showAuthView();
}
