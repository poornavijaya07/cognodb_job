// ==============================================================================
// CognoMatch Frontend Client Script
// Connects to FastAPI Backend with auto-port discovery, full error handling,
// and responsive UI states.
// ==============================================================================

// Candidate Backend Base URLs to auto-probe
const isLocal = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1" || window.location.protocol === "file:";

const CANDIDATE_API_BASES = isLocal
  ? [
      "http://127.0.0.1:8000",
      "http://127.0.0.1:8001",
      "http://localhost:8000",
      "http://localhost:8001",
      window.location.origin
    ]
  : [
      window.location.origin,
      "http://127.0.0.1:8000"
    ];

let API_BASE = isLocal ? "http://127.0.0.1:8000" : window.location.origin;

// DOM Elements
const connectionBadge = document.getElementById("connectionBadge");
const connectionText = document.getElementById("connectionText");
const candidateSelect = document.getElementById("candidateSelect");
const candidateInput = document.getElementById("candidateInput");
const searchBtn = document.getElementById("searchBtn");
const matchForm = document.getElementById("matchForm");

const candidateProfileCard = document.getElementById("candidateProfileCard");
const profileName = document.getElementById("profileName");
const profileEmail = document.getElementById("profileEmail");
const profileExp = document.getElementById("profileExp");
const profileSkillsList = document.getElementById("profileSkillsList");

const metricsBar = document.getElementById("metricsBar");
const metricJobsCount = document.getElementById("metricJobsCount");
const metricTopMatch = document.getElementById("metricTopMatch");
const metricAvgMatch = document.getElementById("metricAvgMatch");

const filterBar = document.getElementById("filterBar");
const resultsCandidateId = document.getElementById("resultsCandidateId");
const matchFilter = document.getElementById("matchFilter");

const initialState = document.getElementById("initialState");
const loadingState = document.getElementById("loadingState");
const noResultsState = document.getElementById("noResultsState");
const jobGrid = document.getElementById("jobGrid");

const errorBanner = document.getElementById("errorBanner");
const errorTitle = document.getElementById("errorTitle");
const errorMessage = document.getElementById("errorMessage");
const errorClose = document.getElementById("errorClose");

// App State
let allMatches = [];
let candidateCache = {};

// ==============================================================================
// Initialization
// ==============================================================================

document.addEventListener("DOMContentLoaded", async () => {
  setupEventListeners();
  await initHealthCheck();
  await loadCandidatesList();
});

function setupEventListeners() {
  // Candidate Select Change
  candidateSelect.addEventListener("change", (e) => {
    const selectedId = e.target.value;
    if (selectedId) {
      candidateInput.value = selectedId;
      displayCandidateProfilePreview(selectedId);
      dismissError();
    }
  });

  // Candidate Input Typing
  candidateInput.addEventListener("input", (e) => {
    const val = e.target.value.trim().toUpperCase();
    if (candidateCache[val]) {
      candidateSelect.value = val;
      displayCandidateProfilePreview(val);
    }
    dismissError();
  });

  // Search Button Click / Form Submit
  matchForm.addEventListener("submit", (e) => {
    e.preventDefault();
    handleFindMatches();
  });

  // Error Close
  errorClose.addEventListener("click", dismissError);

  // Match Filter Change
  matchFilter.addEventListener("change", () => {
    renderJobCards();
  });

  // Allow clicking connection badge to re-test connection
  connectionBadge.addEventListener("click", () => {
    initHealthCheck();
    loadCandidatesList();
  });
}

// ==============================================================================
// Dynamic Backend Auto-Discovery & Health Check
// ==============================================================================

async function detectWorkingApiBase() {
  for (const base of CANDIDATE_API_BASES) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 1200);
      const res = await fetch(`${base}/health`, { signal: controller.signal });
      clearTimeout(timeoutId);
      if (res.ok) {
        const data = await res.json();
        if (data.status === "healthy" || data.database === "connected") {
          API_BASE = base;
          return base;
        }
      }
    } catch (e) {
      // Continue probing other candidate ports
    }
  }
  return API_BASE;
}

async function initHealthCheck() {
  connectionBadge.className = "status-badge status-checking";
  connectionText.textContent = "Connecting to CognoDB...";

  const workingBase = await detectWorkingApiBase();
  try {
    const res = await fetch(`${workingBase}/health`);
    if (res.ok) {
      API_BASE = workingBase;
      connectionBadge.className = "status-badge status-online";
      connectionText.textContent = "CognoDB Connected";
      return true;
    } else {
      throw new Error(`Server returned status ${res.status}`);
    }
  } catch (err) {
    connectionBadge.className = "status-badge status-offline";
    connectionText.textContent = "Backend Offline (Click to Retry)";
    return false;
  }
}

async function loadCandidatesList() {
  try {
    const res = await fetch(`${API_BASE}/candidates`);
    if (!res.ok) throw new Error("Failed to load candidates");
    const candidates = await res.json();

    candidateSelect.innerHTML = '<option value="" disabled selected>Select candidate profile...</option>';
    candidateCache = {};

    candidates.forEach((c) => {
      candidateCache[c.id] = c;
      const opt = document.createElement("option");
      opt.value = c.id;
      opt.textContent = `${c.name} (${c.id}) — ${c.yearsExperience} yrs exp`;
      candidateSelect.appendChild(opt);
    });

    // Default select first candidate for seamless initial experience
    if (candidates.length > 0) {
      candidateSelect.value = candidates[0].id;
      candidateInput.value = candidates[0].id;
      displayCandidateProfilePreview(candidates[0].id);
    }
  } catch (err) {
    candidateSelect.innerHTML = '<option value="" disabled>Error loading candidates</option>';
  }
}

function displayCandidateProfilePreview(candidateId) {
  const candidate = candidateCache[candidateId];
  if (!candidate) {
    candidateProfileCard.classList.add("hidden");
    return;
  }

  profileName.textContent = candidate.name || candidateId;
  profileEmail.textContent = candidate.email || `${candidateId.toLowerCase()}@example.com`;
  profileExp.textContent = `${candidate.yearsExperience || 0} yrs exp`;

  profileSkillsList.innerHTML = "";
  const skills = candidate.skills || [];
  if (skills.length > 0) {
    skills.forEach((skill) => {
      const tag = document.createElement("span");
      tag.className = "skill-tag";
      tag.textContent = skill;
      profileSkillsList.appendChild(tag);
    });
  } else {
    profileSkillsList.innerHTML = '<span class="text-dim">No skills registered</span>';
  }

  candidateProfileCard.classList.remove("hidden");
}

// ==============================================================================
// Matching Logic Execution
// ==============================================================================

async function handleFindMatches() {
  const candidateId = (candidateInput.value || candidateSelect.value || "").trim().toUpperCase();

  if (!candidateId) {
    showError("Missing Candidate ID", "Please select a candidate or enter a valid Candidate ID (e.g. C001).");
    return;
  }

  dismissError();
  showLoading();

  try {
    // 1. Fetch Candidate details (if not already cached)
    if (!candidateCache[candidateId]) {
      try {
        const candRes = await fetch(`${API_BASE}/candidates/${candidateId}`);
        if (candRes.ok) {
          const candData = await candRes.json();
          candidateCache[candidateId] = candData;
          displayCandidateProfilePreview(candidateId);
        }
      } catch (e) {
        // Continue to match call
      }
    } else {
      displayCandidateProfilePreview(candidateId);
    }

    // 2. Fetch Graph-based Job Recommendations
    const res = await fetch(`${API_BASE}/match/${candidateId}`);

    if (res.status === 404) {
      const err = await res.json().catch(() => ({ detail: "Candidate not found." }));
      showError("Candidate Not Found", err.detail || `Candidate '${candidateId}' was not found in CognoDB.`);
      showInitial();
      return;
    }

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Error fetching matches" }));
      showError("Server Error", err.detail || `Backend returned status ${res.status}`);
      showInitial();
      return;
    }

    const matches = await res.json();
    allMatches = matches;

    resultsCandidateId.textContent = candidateCache[candidateId]?.name || candidateId;

    if (!matches || matches.length === 0) {
      showNoResults();
    } else {
      updateMetrics(matches);
      renderJobCards();
      showResults();
    }
  } catch (err) {
    showError("Connection Failed", "Unable to communicate with the CognoDB backend API. Please make sure the FastAPI server is running.");
    showInitial();
  }
}

// ==============================================================================
// Rendering & UI State Handlers
// ==============================================================================

function updateMetrics(matches) {
  metricJobsCount.textContent = matches.length;

  if (matches.length > 0) {
    const highest = Math.max(...matches.map((m) => m.matchPercentage || 0));
    const avg = matches.reduce((acc, m) => acc + (m.matchPercentage || 0), 0) / matches.length;

    metricTopMatch.textContent = `${Math.round(highest)}%`;
    metricAvgMatch.textContent = `${Math.round(avg)}%`;
  } else {
    metricTopMatch.textContent = "0%";
    metricAvgMatch.textContent = "0%";
  }
}

function renderJobCards() {
  const filterVal = matchFilter.value;
  let filtered = [...allMatches];

  if (filterVal === "75") {
    filtered = filtered.filter((m) => m.matchPercentage >= 75);
  } else if (filterVal === "50") {
    filtered = filtered.filter((m) => m.matchPercentage >= 50);
  }

  jobGrid.innerHTML = "";

  if (filtered.length === 0) {
    jobGrid.innerHTML = `
      <div class="state-container" style="padding: 30px 20px;">
        <p>No jobs match the selected filter criteria (${filterVal}%+).</p>
      </div>
    `;
    return;
  }

  filtered.forEach((job) => {
    const pct = job.matchPercentage || 0;
    let scoreClass = "low";
    let pillClass = "pill-low";
    let barClass = "bar-low";

    if (pct >= 75) {
      scoreClass = "high";
      pillClass = "pill-high";
      barClass = "bar-high";
    } else if (pct >= 50) {
      scoreClass = "medium";
      pillClass = "pill-medium";
      barClass = "bar-medium";
    }

    const card = document.createElement("div");
    card.className = `job-card match-${scoreClass}`;

    // Matching skills HTML
    const matchingSkillsHtml = (job.matchingSkills || [])
      .map((s) => `<span class="skill-tag matched">${s}</span>`)
      .join("");

    // Missing skills HTML
    const missingSkillsHtml = (job.missingSkills || [])
      .map((s) => `<span class="skill-tag missing">${s}</span>`)
      .join("");

    card.innerHTML = `
      <div class="job-card-top">
        <div class="job-meta-main">
          <h4>${job.title}</h4>
          <div class="job-company">
            <span><strong>${job.company || "Hiring Partner"}</strong></span>
            <span class="dot-sep">&bull;</span>
            <span>${job.location || "Remote"}</span>
            <span class="dot-sep">&bull;</span>
            <span class="badge badge-primary">${job.jobId}</span>
          </div>
        </div>

        <div class="job-match-score">
          <div class="match-pill ${pillClass}">
            <span>${pct}% Match</span>
          </div>
          <span class="match-subtext">${job.matchCount} of ${job.requiredSkillCount} skills matched</span>
        </div>
      </div>

      <div class="match-progress-track">
        <div class="match-progress-bar ${barClass}" style="width: ${pct}%;"></div>
      </div>

      <div class="job-skills-section">
        <div class="skills-group">
          <span class="skills-group-label">Matched:</span>
          <div class="skills-wrap">${matchingSkillsHtml || '<span class="text-dim">None</span>'}</div>
        </div>
        ${
          missingSkillsHtml
            ? `
        <div class="skills-group">
          <span class="skills-group-label">Missing:</span>
          <div class="skills-wrap">${missingSkillsHtml}</div>
        </div>`
            : ""
        }
      </div>
    `;

    jobGrid.appendChild(card);
  });
}

function showLoading() {
  initialState.classList.add("hidden");
  noResultsState.classList.add("hidden");
  jobGrid.classList.add("hidden");
  metricsBar.classList.add("hidden");
  filterBar.classList.add("hidden");
  loadingState.classList.remove("hidden");
}

function showResults() {
  initialState.classList.add("hidden");
  loadingState.classList.add("hidden");
  noResultsState.classList.add("hidden");
  metricsBar.classList.remove("hidden");
  filterBar.classList.remove("hidden");
  jobGrid.classList.remove("hidden");
}

function showInitial() {
  loadingState.classList.add("hidden");
  noResultsState.classList.add("hidden");
  jobGrid.classList.add("hidden");
  metricsBar.classList.add("hidden");
  filterBar.classList.add("hidden");
  initialState.classList.remove("hidden");
}

function showNoResults() {
  initialState.classList.add("hidden");
  loadingState.classList.add("hidden");
  jobGrid.classList.add("hidden");
  metricsBar.classList.add("hidden");
  filterBar.classList.add("hidden");
  noResultsState.classList.remove("hidden");
}

function showError(title, msg) {
  errorTitle.textContent = title;
  errorMessage.textContent = msg;
  errorBanner.classList.remove("hidden");
}

function dismissError() {
  errorBanner.classList.add("hidden");
}
