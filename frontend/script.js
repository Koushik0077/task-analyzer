// API base URL - will be set from config.js
const API_BASE = typeof API_BASE_URL !== 'undefined' ? API_BASE_URL : "http://localhost:8000/api/tasks";

const tasks = [];
let nextAutoId = 1;
let analyzedTasks = [];

const form = document.getElementById("task-form");
const bulkTextarea = document.getElementById("bulk-json");
const loadBulkBtn = document.getElementById("load-bulk");
const strategySelect = document.getElementById("strategy");
const analyzeBtn = document.getElementById("analyze-btn");
const top3Btn = document.getElementById("top3-btn");
const clearAllBtn = document.getElementById("clear-all-btn");
const feedbackEl = document.getElementById("feedback");
const currentTasksList = document.getElementById("current-tasks-list");
const taskCountEl = document.getElementById("task-count");
const recommendationsContainer = document.getElementById("recommendations-container");
const strategyDescEl = document.getElementById("strategy-desc");

const strategyDescriptions = {
  smart_balance: "Balances all factors: urgency, importance, effort, and dependencies.",
  fastest_wins: "Prioritizes low-effort tasks to maximize quick wins and momentum.",
  high_impact: "Emphasizes importance over other factors for maximum impact.",
  deadline_driven: "Focuses on urgency and due dates to meet deadlines."
};

function setFeedback(message, type = "") {
  feedbackEl.textContent = message;
  feedbackEl.className = "notification";
  if (type) {
    feedbackEl.classList.add(type);
  }
  // Auto-hide after 4 seconds
  if (message) {
    setTimeout(() => {
      feedbackEl.textContent = "";
      feedbackEl.className = "notification";
    }, 4000);
  }
}

function parseDependencies(text) {
  if (!text.trim()) return [];
  return text
    .split(",")
    .map((d) => d.trim())
    .filter(Boolean);
}

function updateTaskCount() {
  taskCountEl.textContent = tasks.length;
}

function renderCurrentTasks() {
  if (tasks.length === 0) {
    currentTasksList.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">📭</div>
        <p>Your task queue is empty</p>
        <span>Add tasks to get started</span>
      </div>
    `;
    return;
  }

  currentTasksList.innerHTML = tasks.map((task, index) => `
    <div class="task-item">
      <div class="task-info">
        <strong>${task.title}</strong>
        <div class="task-details">
          <span>Due: ${task.due_date || "Not set"}</span>
          <span>Hours: ${task.estimated_hours || 0}</span>
          <span>Importance: ${task.importance || 5}/10</span>
        </div>
      </div>
      <button class="btn-remove" onclick="removeTask(${index})">Remove</button>
    </div>
  `).join("");
}

function removeTask(index) {
  tasks.splice(index, 1);
  updateTaskCount();
  renderCurrentTasks();
  setFeedback("Task removed.", "success");
}

strategySelect.addEventListener("change", () => {
  strategyDescEl.textContent = strategyDescriptions[strategySelect.value] || "";
});

form.addEventListener("submit", (event) => {
  event.preventDefault();

  const title = document.getElementById("title").value.trim();
  const dueDate = document.getElementById("due_date").value || null;
  const estHoursStr = document.getElementById("estimated_hours").value.trim();
  const importanceStr = document.getElementById("importance").value.trim();
  const depsStr = document.getElementById("dependencies").value;

  if (!title) {
    setFeedback("Title is required.", "error");
    return;
  }

  let estimated_hours = parseFloat(estHoursStr || "1");
  if (Number.isNaN(estimated_hours) || estimated_hours < 0) {
    setFeedback("Estimated hours must be a non-negative number.", "error");
    return;
  }

  let importance = parseInt(importanceStr || "5", 10);
  if (Number.isNaN(importance) || importance < 1 || importance > 10) {
    setFeedback("Importance must be between 1 and 10.", "error");
    return;
  }

  const id = `t${nextAutoId++}`;
  const task = {
    id,
    title,
    due_date: dueDate || null,
    estimated_hours,
    importance,
    dependencies: parseDependencies(depsStr),
  };

  tasks.push(task);
  updateTaskCount();
  renderCurrentTasks();
  setFeedback(`Task "${title}" added successfully.`, "success");
  form.reset();
});

loadBulkBtn.addEventListener("click", () => {
  const text = bulkTextarea.value.trim();
  if (!text) {
    setFeedback("Please paste a JSON array of tasks.", "error");
    return;
  }

  try {
    const arr = JSON.parse(text);
    if (!Array.isArray(arr)) {
      throw new Error("JSON must be an array");
    }

    arr.forEach((t) => {
      if (!t.title) {
        return;
      }
      const id = t.id || `t${nextAutoId++}`;
      tasks.push({
        id,
        title: t.title,
        due_date: t.due_date || null,
        estimated_hours: t.estimated_hours ?? 1,
        importance: t.importance ?? 5,
        dependencies: Array.isArray(t.dependencies) ? t.dependencies : [],
      });
    });

    updateTaskCount();
    renderCurrentTasks();
    setFeedback(`Loaded ${arr.length} task(s) from JSON.`, "success");
  } catch (err) {
    console.error(err);
    setFeedback("Invalid JSON: " + err.message, "error");
  }
});

clearAllBtn.addEventListener("click", () => {
  if (tasks.length === 0) {
    setFeedback("No tasks to clear.", "error");
    return;
  }
  if (confirm("Are you sure you want to clear all tasks?")) {
    tasks.length = 0;
    analyzedTasks = [];
    updateTaskCount();
    renderCurrentTasks();
    recommendationsContainer.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">🔍</div>
        <p>Run analysis to see recommendations</p>
      </div>
    `;
    setFeedback("All tasks cleared.", "success");
  }
});

analyzeBtn.addEventListener("click", async () => {
  if (tasks.length === 0) {
    setFeedback("Add at least one task before analyzing.", "error");
    return;
  }
  await callAnalyze(false);
});

top3Btn.addEventListener("click", () => {
  if (analyzedTasks.length === 0) {
    setFeedback("Please run analysis first to see top 3 recommendations.", "error");
    return;
  }
  renderRecommendations(analyzedTasks.slice(0, 3));
  setFeedback("Showing top 3 recommendations.", "success");
});

async function callAnalyze(showTop3Only = false) {
  const strategy = strategySelect.value;

  setFeedback("Analyzing tasks...", "loading");
  analyzeBtn.disabled = true;
  top3Btn.disabled = true;

  try {
    const payload = {
      strategy,
      tasks: tasks,
    };

    const res = await fetch(`${API_BASE}/analyze/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const errText = await res.text();
      throw new Error(errText || "Analysis failed");
    }

    const data = await res.json();
    analyzedTasks = data.tasks || [];
    
    if (showTop3Only) {
      renderRecommendations(analyzedTasks.slice(0, 3));
      setFeedback(`Analysis complete. Showing top 3 recommendations.`, "success");
    } else {
      renderRecommendations(analyzedTasks);
      setFeedback(`Analysis complete. Showing all ${analyzedTasks.length} task(s).`, "success");
    }
  } catch (err) {
    console.error(err);
    const msg =
      err instanceof TypeError
        ? "Failed to reach backend. Make sure the Django server is running on http://localhost:8000"
        : err.message || "Unexpected error";
    setFeedback(msg, "error");
  } finally {
    analyzeBtn.disabled = false;
    top3Btn.disabled = false;
  }
}

function formatDate(dateStr) {
  if (!dateStr) return "Not set";
  const date = new Date(dateStr);
  const today = new Date();
  const tomorrow = new Date(today);
  tomorrow.setDate(tomorrow.getDate() + 1);
  
  if (date.toDateString() === today.toDateString()) {
    return `${dateStr} (Due today)`;
  } else if (date.toDateString() === tomorrow.toDateString()) {
    return `${dateStr} (Due tomorrow)`;
  }
  return dateStr;
}

function calculateMetrics(task) {
  // Extract scores from explanation or calculate from task data
  const score = task.score || 0;
  
  // Parse explanation to extract individual scores
  const explanation = task.explanation || "";
  let urgency = 50;
  let effort = 50;
  let dependency = 10;
  
  // Try to extract urgency score from explanation
  const urgencyMatch = explanation.match(/Urgency.*?score[:\s]+([\d.]+)/i);
  if (urgencyMatch) {
    urgency = parseFloat(urgencyMatch[1]) * 100;
  } else if (task.due_date) {
    const daysUntil = Math.ceil((new Date(task.due_date) - new Date()) / (1000 * 60 * 60 * 24));
    if (daysUntil < 0) urgency = 100;
    else if (daysUntil === 0) urgency = 95;
    else if (daysUntil <= 3) urgency = 85;
    else if (daysUntil <= 7) urgency = 70;
    else urgency = 50;
  }
  
  // Try to extract effort score
  const effortMatch = explanation.match(/effort.*?score[:\s]+([\d.]+)/i);
  if (effortMatch) {
    effort = parseFloat(effortMatch[1]) * 100;
  } else {
    // Calculate based on hours
    const hours = task.estimated_hours || 1;
    effort = Math.max(10, Math.min(100, 100 - (hours * 10)));
  }
  
  // Try to extract dependency score
  const depMatch = explanation.match(/(\d+)\s+task\(s\)\s+depend/i);
  if (depMatch) {
    dependency = Math.min(100, 30 + (parseInt(depMatch[1]) * 20));
  }
  
  const importance = (task.importance / 10) * 100;
  
  return {
    overall: (score * 100).toFixed(1),
    urgency: urgency.toFixed(1),
    importance: importance.toFixed(1),
    effort: effort.toFixed(1),
    dependency: dependency.toFixed(1)
  };
}

function renderRecommendations(recommendedTasks) {
  if (!recommendedTasks || recommendedTasks.length === 0) {
    recommendationsContainer.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">🔍</div>
        <p>Run analysis to see recommendations</p>
      </div>
    `;
    return;
  }

  const isTop3 = recommendedTasks.length <= 3;
  
  recommendationsContainer.innerHTML = recommendedTasks.map((task, index) => {
    const metrics = calculateMetrics(task);
    const priority = (task.priority_label || "Medium").toLowerCase();
    const priorityClass = priority === "high" ? "high" : priority === "low" ? "low" : "medium";
    const position = index + 1;
    
    // Extract suggestion text from explanation
    const explanation = task.explanation || "";
    let suggestionText = "Recommended based on balanced factors.";
    
    // Try to extract key reasons from explanation
    const reasons = [];
    if (explanation.includes("Overdue") || explanation.includes("due today")) {
      reasons.push("urgent deadline");
    }
    if (explanation.includes("Due in")) {
      const daysMatch = explanation.match(/Due in (\d+)d/);
      if (daysMatch) {
        const days = parseInt(daysMatch[1]);
        if (days <= 3) reasons.push(`due in ${days} day(s)`);
      }
    }
    if (explanation.includes("quick win") || explanation.includes("low-effort")) {
      reasons.push("short task");
    }
    if (explanation.includes("high importance") || task.importance >= 8) {
      reasons.push("high importance");
    }
    if (explanation.includes("depend on this")) {
      reasons.push("blocks other tasks");
    }
    
    if (reasons.length > 0) {
      suggestionText = `Recommended based on balanced factors. Priority due to: ${reasons.join(", ")}.`;
    }

    return `
      <div class="recommendation-card priority-${priorityClass}">
        <div class="recommendation-badge">#${position}</div>
        <div class="recommendation-header">
          <h4>${task.title || "Untitled Task"}</h4>
          <span class="priority-badge priority-${priorityClass}">${task.priority_label || "Medium"} Priority</span>
        </div>
        
        <div class="priority-score">
          Priority Score: <strong>${metrics.overall}</strong>
        </div>
        
        <p class="suggestion-text">
          ${isTop3 ? `Suggestion #${position}: ` : `Rank #${position}: `}${suggestionText}
        </p>
        
        <div class="task-metrics">
          <div class="metric-item">
            <span class="metric-label">OVERALL:</span>
            <span class="metric-value">${metrics.overall}</span>
          </div>
          <div class="metric-item">
            <span class="metric-label">URGENCY:</span>
            <span class="metric-value">${metrics.urgency}</span>
          </div>
          <div class="metric-item">
            <span class="metric-label">IMPORTANCE:</span>
            <span class="metric-value">${metrics.importance}</span>
          </div>
          <div class="metric-item">
            <span class="metric-label">EFFORT:</span>
            <span class="metric-value">${metrics.effort}</span>
          </div>
          <div class="metric-item">
            <span class="metric-label">DEPENDENCY:</span>
            <span class="metric-value">${metrics.dependency}</span>
          </div>
        </div>
        
        <div class="task-details-icons">
          <div class="detail-item">
            <span class="icon">📅</span>
            <span>Due: ${formatDate(task.due_date)}</span>
          </div>
          <div class="detail-item">
            <span class="icon">⏱️</span>
            <span>Effort: ${task.estimated_hours || 0} hour(s)</span>
          </div>
          <div class="detail-item">
            <span class="icon">⭐</span>
            <span>Importance: ${task.importance || 5}/10</span>
          </div>
        </div>
      </div>
    `;
  }).join("");
}

// Initialize
updateTaskCount();
renderCurrentTasks();
strategyDescEl.textContent = strategyDescriptions[strategySelect.value];
