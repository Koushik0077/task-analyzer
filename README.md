## Smart Task Analyzer – Singularium Assignment

This project implements a **Smart Task Analyzer** using **Python, Django, Django REST Framework, and vanilla HTML/CSS/JavaScript**. It exposes a backend API that scores tasks by priority and a small frontend that lets users add tasks, select a strategy, and view ranked results.

---

### Setup Instructions

1. **Backend**

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate  # on Windows PowerShell
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/tasks/`.

2. **Frontend**

Open `frontend/index.html` in your browser (for strict CORS you can serve it via a simple static server, but for this assignment opening from file usually works).

---

### API Overview

- `POST /api/tasks/analyze/`
  - Body:
    ```json
    {
      "strategy": "smart_balance",
      "tasks": [
        {
          "id": "t1",
          "title": "Fix login bug",
          "due_date": "2025-11-30",
          "estimated_hours": 3,
          "importance": 8,
          "dependencies": []
        }
      ]
    }
    ```
  - Returns the same tasks **sorted by descending priority score**, with extra fields: `score`, `priority_label`, `explanation`, and `warnings`.

- `GET /api/tasks/suggest/?limit=3`
  - Returns the top N (default 3) tasks **from the last analysis**.
  - For stateless usage there is also `POST /api/tasks/suggest/` with the same body as `/analyze/`; it returns only the top 3 tasks.

---

### Priority Algorithm (summary)

Each task is converted into an internal structure with: title, due date, estimated hours, importance, and dependencies. The algorithm computes four sub‑scores—**urgency**, **importance**, **effort**, and **dependency impact**—and then combines them with different weightings for each strategy.

- **Urgency** uses the due date relative to today. Overdue tasks get the strongest boost, tasks due today are very urgent, tasks due within 3–7 days get medium urgency, and further dates get a smaller boost. Tasks without a due date get a mild default urgency so they are not ignored.
- **Importance** normalizes the 1–10 importance field into a 0.1–1.0 score, so more important tasks clearly rank higher.
- **Effort** uses an inverse function of estimated hours, rewarding smaller tasks as “quick wins” with diminishing returns so very tiny tasks do not dominate.
- **Dependencies** build a small graph: a task’s dependency score grows with how many other tasks depend on it, because finishing such tasks can unblock more work. A depth‑first search detects circular dependencies and attaches human‑readable warnings.

These sub-scores are then combined using different **weight profiles**:

- **Fastest Wins**: heavily weights effort (low hours).
- **High Impact**: heavily weights importance.
- **Deadline Driven**: heavily weights urgency.
- **Smart Balance**: balances all four factors for a more holistic priority.

The final numeric score is mapped to a simple High/Medium/Low label. Each task also includes an explanation string describing how each sub‑score contributed, making the algorithm explainable and easy to tweak.

---

### Design Decisions & Trade-offs

- The backend treats tasks as JSON in each request, which keeps the API stateless and simple for the assignment. A `Task` model exists for future persistence but is not required for core behavior.
- `GET /suggest/` returns suggestions from the most recent `/analyze/` call using a simple in‑memory cache; this is acceptable for a single-user test environment.
- Different strategies share the same core scoring logic but apply different weightings, which is easy to extend and reason about.
- Circular dependencies are not blocked but flagged in the `warnings` field so users are informed about problematic graphs.

---

### Time Breakdown (example)

- Algorithm design and scoring implementation: ~1.5 hours  
- Django project + API endpoints + serializers: ~1 hour  
- Frontend UI (HTML, CSS, JS, UX details): ~1 hour  
- Tests, documentation, and polishing: ~0.5–1 hour  

---

### Future Improvements

- Persist tasks per user and support multiple workspaces.
- Visualize dependencies and provide an Eisenhower matrix view.
- Consider weekends/holidays and working hours in urgency.
- Extend unit tests to cover more edge cases and strategies.


