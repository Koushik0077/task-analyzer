## Smart Task Analyzer – Singularium Assignment

This project implements a **Smart Task Analyzer** using **Python, Django, Django REST Framework, and vanilla HTML/CSS/JavaScript**. It exposes a backend API that scores tasks by priority and a modern frontend that lets users add tasks, select a strategy, and view ranked results with detailed explanations.

---

### Setup Instructions

1. **Backend**

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate  # on Windows PowerShell
# or: source venv/bin/activate  # on Linux/Mac
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/tasks/`.

2. **Frontend**

You have several options to run the frontend:

- **Option 1 (Simplest)**: Open `frontend/index.html` directly in your browser (double-click the file)
- **Option 2 (VS Code)**: Use VS Code's Live Server extension - right-click `index.html` and select "Open with Live Server"
- **Option 3 (Python Server)**: 
  ```bash
  cd frontend
  python -m http.server 5500
  ```
  Then open `http://localhost:5500/index.html` in your browser
- **Option 4 (Node.js)**: Use `npx serve` or any static file server

**Note**: Make sure the Django backend is running on `http://localhost:8000` before using the frontend.

3. **Running Tests**

```bash
cd backend
python manage.py test
```

This will run all unit tests for the scoring algorithm.

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

### Algorithm Explanation (300-500 words)

The priority scoring algorithm is designed to be transparent, configurable, and aligned with common productivity heuristics. Each task is first converted into a structured internal representation containing the following fields: title, due date (optional), estimated hours, importance rating (1-10), and dependencies (list of task IDs that must be completed first).

The core innovation lies in computing four independent sub-scores that capture different dimensions of task priority, then intelligently combining them using strategy-specific weightings. This multi-factor approach ensures that no single dimension dominates the decision-making process, while still allowing users to emphasize specific factors through strategy selection.

**Urgency scoring** is driven by temporal proximity to deadlines. The algorithm calculates the number of days between the task's due date and today. Tasks that are overdue receive the highest urgency boost, with the score increasing proportionally to how far overdue they are (capped to prevent extreme values). Tasks due today receive a very high urgency score (1.5), while tasks due within the next 3 days get a high score (1.2). Tasks due within a week receive moderate urgency (0.8), and those further into the future get progressively lower scores (0.4). Importantly, tasks without a due date are assigned a mild default urgency (0.3) so they are not completely ignored, but they naturally rank lower than time-sensitive work.

**Importance scoring** directly normalizes the user-provided 1-10 importance rating into a 0.1-1.0 range. This linear mapping makes the importance dimension easy to interpret and compare across tasks. A task rated 10/10 receives a perfect 1.0 importance score, while a 5/10 task gets 0.5, ensuring that user priorities are faithfully reflected in the final ranking.

**Effort scoring** uses an inverse function of estimated hours, rewarding smaller tasks as "quick wins" that can provide momentum. The formula `1.0 / (1.0 + hours / 4.0)` means that a 1-hour task receives a high effort score (~0.8), a 4-hour task gets a medium score (~0.5), and an 8-hour task gets a lower score (~0.33). The diminishing returns prevent extremely tiny tasks from dominating everything, while still providing meaningful differentiation between effort levels.

**Dependency scoring** builds a dependency graph by counting how many other tasks depend on each task. Tasks that unblock multiple other tasks receive a boost because completing them enables more overall progress. The dependency score starts at 0.3 for tasks with no dependents and increases by 0.2 for each dependent task, capped at 1.0. The algorithm also performs a depth-first search to detect circular dependencies, which are flagged in the warnings field rather than blocking execution, allowing users to understand and resolve dependency issues.

These four sub-scores are combined into a single priority score using different weight profiles for each strategy. "Fastest Wins" heavily weights effort (45%) to prioritize quick tasks. "High Impact" emphasizes importance (55%) for maximum value. "Deadline Driven" focuses on urgency (55%) to meet time constraints. "Smart Balance" uses more even weights (35% urgency, 35% importance, 15% effort, 15% dependencies) for a holistic view. The final combined score is mapped to High/Medium/Low priority labels using thresholds (≥1.0 for High, ≥0.6 for Medium), and each task includes a detailed explanation showing how each component contributed, making the algorithm explainable and debuggable.

---

### Design Decisions & Trade-offs

**Stateless API Design**: The backend treats tasks as JSON payloads in each request rather than persisting them to a database. This design choice keeps the API stateless and simple for the assignment scope, eliminating the need for user authentication, session management, or database migrations. While a `Task` model exists in the codebase for potential future extensions, the core functionality works entirely in-memory. This trade-off prioritizes simplicity and rapid development over persistence, which is appropriate for a demonstration project.

**In-Memory Caching for Suggestions**: The `GET /suggest/` endpoint returns recommendations from the most recent `/analyze/` call using a simple module-level variable cache. This approach makes the API intuitive (no request body needed for GET) and avoids requiring clients to store analysis results. However, it's not multi-tenant and doesn't persist across server restarts. For a production system, we would use Redis or database-backed caching with user sessions, but for a single-user assignment, the simplicity is acceptable.

**Strategy-Based Weighting vs. Separate Algorithms**: Rather than implementing completely different algorithms for each strategy, the system uses a single core scoring function with different weight profiles. This design reduces code duplication, makes it easier to add new strategies (just define new weights), and ensures consistency in how factors are calculated. The trade-off is that strategies can't have fundamentally different logic (e.g., a strategy that ignores effort entirely), but this limitation is acceptable given the assignment requirements.

**Circular Dependency Detection vs. Prevention**: The algorithm detects circular dependencies using depth-first search and flags them in warnings, but doesn't prevent analysis from proceeding. This allows users to see all their tasks ranked even if there are dependency issues, and the warnings help them understand and fix the problems. An alternative would be to throw errors or filter out tasks in cycles, but that would be more restrictive and less informative.

**Explainable Scoring**: Each task includes a detailed explanation string showing how urgency, importance, effort, and dependencies contributed to the final score. This transparency helps users understand why tasks are ranked the way they are and makes debugging easier. The trade-off is slightly longer response payloads, but the value in user trust and system debuggability outweighs the minor overhead.

**Priority Label Thresholds**: The algorithm maps numeric scores to High/Medium/Low labels using simple thresholds (≥1.0, ≥0.6). These thresholds were chosen through experimentation to provide meaningful differentiation while ensuring that high-importance tasks (score ≥1.0) reliably get the "High" label. A more sophisticated approach might use percentile-based thresholds or machine learning, but the current approach is transparent and works well for the assignment scope.

---

### Time Breakdown

- **Algorithm design and scoring implementation**: ~1.5 hours
  - Designing the multi-factor scoring approach
  - Implementing urgency, importance, effort, and dependency calculations
  - Building the strategy-based weighting system
  - Adding circular dependency detection

- **Django project setup + API endpoints + serializers**: ~1 hour
  - Setting up Django project structure
  - Creating REST API endpoints with DRF
  - Implementing request/response serializers with validation
  - Adding error handling and edge case management

- **Frontend UI (HTML, CSS, JavaScript)**: ~1.5 hours
  - Building responsive layout with modern dark theme
  - Implementing task input forms and bulk JSON import
  - Creating recommendation cards with metrics display
  - Adding real-time feedback and error handling
  - Ensuring cross-browser compatibility

- **Unit tests and documentation**: ~1 hour
  - Writing comprehensive unit tests for scoring algorithm
  - Creating detailed README with setup instructions
  - Documenting API endpoints and algorithm logic
  - Adding code comments and explanations

**Total**: Approximately 4-5 hours

---

### Bonus Challenges

**Bonus challenges attempted**: None

While the assignment mentioned several interesting bonus features (dependency graph visualization, date intelligence for weekends/holidays, Eisenhower matrix view, learning system, and additional unit tests), I focused on delivering a high-quality core implementation that fully meets all required functionality. The codebase is structured to make these features easy to add in the future—for example, the dependency graph data is already computed and could be visualized, and the scoring algorithm is modular enough to incorporate weekend/holiday logic.

If given more time, I would prioritize:
1. **Dependency Graph Visualization**: Using a library like D3.js or vis.js to render the dependency relationships
2. **Additional Unit Tests**: Expanding test coverage to include edge cases like missing data, invalid inputs, and all four strategies
3. **Date Intelligence**: Enhancing urgency calculations to account for weekends and business hours

---

### Future Improvements

- **Persistence Layer**: Add database persistence for tasks with user authentication and multiple workspaces
- **Dependency Visualization**: Visual dependency graph using D3.js or similar library to show task relationships
- **Eisenhower Matrix View**: Display tasks on a 2D grid (Urgent vs. Important) for alternative prioritization perspective
- **Date Intelligence**: Consider weekends, holidays, and working hours when calculating urgency scores
- **Learning System**: Allow users to mark suggested tasks as helpful/unhelpful and adjust algorithm weights based on feedback
- **Export Functionality**: Export analyzed tasks to CSV, JSON, or PDF formats
- **Task Templates**: Pre-defined task templates for common workflows
- **Batch Operations**: Bulk edit, delete, or update tasks
- **Advanced Filtering**: Filter tasks by priority, due date range, or other criteria
- **Performance Optimization**: Add caching for large task lists and optimize scoring calculations

---

### Testing

The project includes comprehensive unit tests for the scoring algorithm. Run tests with:

```bash
cd backend
python manage.py test
```

**Test Coverage**:
- High importance tasks rank higher than low importance tasks (High Impact strategy)
- Overdue tasks rank higher than future tasks (Deadline Driven strategy)
- Low-effort tasks rank higher than high-effort tasks (Fastest Wins strategy)
- Tasks with dependencies receive appropriate boosts
- Circular dependencies are detected and flagged

All tests pass and validate the core scoring logic across different strategies and edge cases.
