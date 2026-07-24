// app.js — UI logic for Iron Log

const el = (id) => document.getElementById(id);
let currentSessionId = null;
let exercisesCache = [];
let sessionsCache = [];
let calendarViewDate = new Date(); // month currently shown in the calendar widget

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

// Fires the instant a token expires (either from the scheduled expiry
// timer in api.js, or a 401 from any request) — bounces straight back
// to the login screen with no intermediate "loading" state.
Api.onSessionExpired = () => {
  if (!el("auth-view").classList.contains("hidden")) return; // already there
  showAuthView();
  showToast("Session expired. Please log in again.", true);
};

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
    sessionsCache = sessions;
    renderCalendar();

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
      card.dataset.date = s.date;
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

// ---------------- Calendar ----------------
function renderCalendar() {
  const grid = el("calendar-grid");
  const title = el("cal-title");
  const year = calendarViewDate.getFullYear();
  const month = calendarViewDate.getMonth(); // 0-indexed

  title.textContent = calendarViewDate.toLocaleDateString(undefined, { month: "long", year: "numeric" });

  // Map of "YYYY-MM-DD" -> sessions recorded that day
  const byDate = {};
  sessionsCache.forEach((s) => {
    (byDate[s.date] = byDate[s.date] || []).push(s);
  });

  const firstOfMonth = new Date(year, month, 1);
  const startWeekday = firstOfMonth.getDay(); // 0 = Sunday
  const daysInMonth = new Date(year, month + 1, 0).getDate();

  const todayStr = toDateKey(new Date());

  let html = "";

  // Leading blanks so day 1 lands under the correct weekday
  for (let i = 0; i < startWeekday; i++) {
    html += `<div class="calendar-day is-empty"></div>`;
  }

  for (let day = 1; day <= daysInMonth; day++) {
    const dateKey = toDateKey(new Date(year, month, day));
    const hasSession = !!byDate[dateKey];
    const isToday = dateKey === todayStr;
    const classes = ["calendar-day"];
    if (hasSession) classes.push("has-session");
    if (isToday) classes.push("is-today");

    html += `<div class="${classes.join(" ")}" data-date="${dateKey}" title="${hasSession ? `${byDate[dateKey].length} session${byDate[dateKey].length > 1 ? "s" : ""} recorded` : ""}">${day}</div>`;
  }

  grid.innerHTML = html;

  grid.querySelectorAll(".calendar-day.has-session").forEach((cell) => {
    cell.addEventListener("click", () => handleCalendarDayClick(cell.dataset.date, byDate[cell.dataset.date]));
  });
}

function toDateKey(dateObj) {
  const y = dateObj.getFullYear();
  const m = String(dateObj.getMonth() + 1).padStart(2, "0");
  const d = String(dateObj.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

function handleCalendarDayClick(dateKey, sessionsOnDay) {
  if (sessionsOnDay.length === 1) {
    openSessionDetail(sessionsOnDay[0].id);
    return;
  }
  // Multiple sessions on the same day — jump to the list and flash them
  const cards = document.querySelectorAll(`.session-card[data-date="${dateKey}"]`);
  if (!cards.length) return;
  cards[0].scrollIntoView({ behavior: "smooth", block: "center" });
  cards.forEach((card) => {
    card.style.transition = "none";
    card.style.borderColor = "var(--accent)";
    card.style.background = "var(--surface-raised)";
    setTimeout(() => {
      card.style.transition = "border-color 0.6s ease, background 0.6s ease";
      card.style.borderColor = "";
      card.style.background = "";
    }, 50);
  });
}

el("cal-prev").addEventListener("click", () => {
  calendarViewDate = new Date(calendarViewDate.getFullYear(), calendarViewDate.getMonth() - 1, 1);
  renderCalendar();
});
el("cal-next").addEventListener("click", () => {
  calendarViewDate = new Date(calendarViewDate.getFullYear(), calendarViewDate.getMonth() + 1, 1);
  renderCalendar();
});

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
let currentProgressData = null; // full history for the currently selected exercise
let currentProgressRange = "1m"; // "1m" | "6m"
let progressChart = null; // Chart.js instance, so we can destroy/rebuild on update

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

// Range toggle just re-filters/redraws already-fetched data — no refetch needed.
document.querySelectorAll(".range-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".range-btn").forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    currentProgressRange = btn.dataset.range;
    drawProgress();
  });
});

async function renderProgress(exerciseId) {
  const container = el("progress-content");
  container.innerHTML = "<p class='empty-state'>Loading…</p>";
  try {
    currentProgressData = await Api.getExerciseProgress(exerciseId);
    drawProgress();
  } catch (err) {
    showToast(err.message, true);
  }
}

function filterHistoryByRange(history, range) {
  const cutoff = new Date();
  cutoff.setMonth(cutoff.getMonth() - (range === "6m" ? 6 : 1));
  return history.filter((point) => new Date(point.date + "T00:00:00") >= cutoff);
}

function drawProgress() {
  const container = el("progress-content");
  const data = currentProgressData;

  if (!data || !data.history.length) {
    container.innerHTML = "<div class='empty-state'>No sets logged for this exercise yet.</div>";
    return;
  }

  const filtered = filterHistoryByRange(data.history, currentProgressRange);

  let html = `
    <div class="progress-summary">
      <div class="pb-block">
        <div class="pb-value">${data.personal_best_weight}kg</div>
        <div class="pb-label">Personal best</div>
      </div>
    </div>
    <div class="progress-chart-card">
      <canvas id="progress-chart-canvas"></canvas>
    </div>
  `;

  if (!filtered.length) {
    html += `<div class="empty-state">No sets logged in this time frame.</div>`;
  } else {
    html += `<div class="progress-history">`;
    [...filtered].reverse().forEach((point) => {
      html += `<div class="progress-row">
        <span class="row-date">${formatDate(point.date)}</span>
        <span class="row-max">${point.max_weight}kg</span>
        <span>${point.total_sets} sets</span>
        <span>${point.total_volume}kg vol</span>
      </div>`;
    });
    html += `</div>`;
  }

  container.innerHTML = html;
  renderProgressChart(filtered);
}

function renderProgressChart(points) {
  const canvas = el("progress-chart-canvas");
  if (!canvas) return;

  if (progressChart) {
    progressChart.destroy();
    progressChart = null;
  }
  if (!points.length) return;

  const styles = getComputedStyle(document.documentElement);
  const accent = styles.getPropertyValue("--accent").trim();
  const accentGlow = styles.getPropertyValue("--accent-glow").trim();
  const textMuted = styles.getPropertyValue("--text-muted").trim();
  const border = styles.getPropertyValue("--border").trim();
  const surfaceRaised = styles.getPropertyValue("--surface-raised").trim();

  progressChart = new Chart(canvas.getContext("2d"), {
    type: "line",
    data: {
      labels: points.map((p) =>
        new Date(p.date + "T00:00:00").toLocaleDateString(undefined, { month: "short", day: "numeric" })
      ),
      datasets: [
        {
          label: "Max weight (kg)",
          data: points.map((p) => p.max_weight),
          borderColor: accent,
          backgroundColor: accentGlow,
          pointBackgroundColor: accent,
          pointBorderColor: accent,
          pointRadius: points.length > 25 ? 0 : 3,
          pointHoverRadius: 5,
          borderWidth: 2,
          tension: 0.25,
          fill: true,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: surfaceRaised,
          borderColor: border,
          borderWidth: 1,
          titleColor: "#F3F1EC",
          bodyColor: "#F3F1EC",
          padding: 10,
          displayColors: false,
          callbacks: {
            label: (ctx) => `${ctx.parsed.y}kg`,
          },
        },
      },
      scales: {
        x: {
          grid: { color: border, drawTicks: false },
          ticks: { color: textMuted, font: { family: "JetBrains Mono", size: 11 }, maxRotation: 0 },
        },
        y: {
          grid: { color: border, drawTicks: false },
          ticks: {
            color: textMuted,
            font: { family: "JetBrains Mono", size: 11 },
            callback: (val) => `${val}kg`,
          },
        },
      },
    },
  });
}

// ---------------- Boot ----------------
// Check the token's exp claim locally before rendering anything — this
// is synchronous, so there's no network round trip and no "loading
// session…" flash. An expired (or missing) token goes straight to the
// login screen; a valid one also gets its auto-expiry timer armed
// (done inside Api.setToken/isTokenValid) so a session that expires
// while the app is open kicks the user out immediately, not just on
// their next API call.
if (Api.isTokenValid()) {
  Api._scheduleExpiryLogout(Api.getToken());
  showAppView();
} else {
  Api.clearToken();
  showAuthView();
}