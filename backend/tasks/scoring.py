from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Dict, List, Tuple, Set, Any


@dataclass
class TaskData:
    id: str
    title: str
    due_date: date | None
    estimated_hours: float
    importance: int
    dependencies: List[str]


def _days_until(d: date | None, today: date) -> float | None:
    if d is None:
        return None
    delta = (d - today).days
    return float(delta)


def _urgency_score(task: TaskData, today: date) -> Tuple[float, str]:
    """
    Higher is more urgent.
    - Overdue: strongest boost
    - Due soon: medium boost
    - Far away: smaller score
    - No due date: neutral
    """
    days = _days_until(task.due_date, today)
    if days is None:
        return 0.3, "• Urgency: No due date set, assigned default low urgency score (0.3)"

    if days < 0:
        overdue_days = abs(days)
        score = 1.0 + min(overdue_days / 7.0, 1.0)  # cap at 2.0
        if overdue_days <= 7:
            return score, f"• Urgency: Task is overdue by {overdue_days} day(s). High urgency boost applied (score: {score:.2f})"
        return score, f"• Urgency: Task is significantly overdue by {overdue_days} day(s). Maximum urgency boost applied (score: {score:.2f})"
    if days == 0:
        return 1.5, "• Urgency: Task is due today. Very high urgency score (1.5) applied"
    if days <= 3:
        return 1.2, f"• Urgency: Task due in {int(days)} day(s). High urgency score (1.2) - needs immediate attention"
    if days <= 7:
        return 0.8, f"• Urgency: Task due in {int(days)} day(s). Moderate urgency score (0.8) - approaching deadline"
    return 0.4, f"• Urgency: Task due in {int(days)} day(s). Lower urgency score (0.4) - deadline is further away"


def _importance_score(task: TaskData) -> Tuple[float, str]:
    # Normalize 1–10 importance to 0.1–1.0
    score = max(1, min(task.importance, 10)) / 10.0
    if task.importance >= 8:
        level = "very high"
    elif task.importance >= 6:
        level = "high"
    elif task.importance >= 4:
        level = "medium"
    else:
        level = "low"
    return score, f"• Importance: Rated {task.importance}/10 ({level} priority). Normalized score: {score:.2f}"


def _effort_score(task: TaskData) -> Tuple[float, str]:
    """
    Small effort → higher score.
    We use a simple inverse function with diminishing returns.
    """
    h = max(task.estimated_hours, 0.1)
    score = 1.0 / (1.0 + h / 4.0)  # 4 hours ~ medium
    if task.estimated_hours <= 2:
        effort_level = "quick win"
    elif task.estimated_hours <= 5:
        effort_level = "moderate effort"
    else:
        effort_level = "high effort"
    return score, f"• Effort: Estimated {task.estimated_hours} hour(s) ({effort_level}). Lower effort = higher score ({score:.2f})"


def _dependency_scores(tasks: Dict[str, TaskData]) -> Tuple[Dict[str, float], Dict[str, str], List[str]]:
    """
    - Compute how many tasks depend on each task (out-degree).
    - Detect circular dependencies using DFS.
    Returns:
      dep_score_by_id, explanation_by_id, warnings (including cycles).
    """
    dependents: Dict[str, List[str]] = {tid: [] for tid in tasks.keys()}
    for t in tasks.values():
        for dep_id in t.dependencies:
            if dep_id in dependents:
                dependents[dep_id].append(t.id)

    dep_score: Dict[str, float] = {}
    dep_expl: Dict[str, str] = {}
    for tid, dependents_list in dependents.items():
        count = len(dependents_list)
        dep_score[tid] = min(1.0, 0.3 + 0.2 * count)  # mild boost up to 1.0
        if count == 0:
            dep_expl[tid] = "• Dependencies: No other tasks depend on this task. No dependency boost applied"
        else:
            dep_expl[tid] = f"• Dependencies: {count} task(s) depend on completing this task. Dependency boost score: {dep_score[tid]:.2f} (unblocks other work)"

    # Cycle detection
    warnings: List[str] = []
    visited: Set[str] = set()
    stack: Set[str] = set()

    def dfs(tid: str, path: List[str]):
        visited.add(tid)
        stack.add(tid)
        for dep in tasks[tid].dependencies:
            if dep not in tasks:
                continue
            if dep not in visited:
                dfs(dep, path + [dep])
            elif dep in stack:
                cycle_path = path + [dep]
                warnings.append(f"Circular dependency detected: {' -> '.join(cycle_path)}")
        stack.remove(tid)

    for tid in tasks.keys():
        if tid not in visited:
            dfs(tid, [tid])

    return dep_score, dep_expl, warnings


def _combine_scores(
    t: TaskData,
    urgency: float,
    importance: float,
    effort: float,
    dependency: float,
    strategy: str,
) -> Tuple[float, str]:
    """
    Combine sub-scores according to chosen strategy.
    """
    if strategy == "fastest_wins":
        weights = dict(u=0.2, im=0.2, ef=0.45, dep=0.15)
        desc = "Fastest Wins"
        strategy_desc = "Prioritizes low-effort tasks (45% weight on effort) for quick wins"
    elif strategy == "high_impact":
        weights = dict(u=0.2, im=0.55, ef=0.1, dep=0.15)
        desc = "High Impact"
        strategy_desc = "Emphasizes importance (55% weight) over other factors"
    elif strategy == "deadline_driven":
        weights = dict(u=0.55, im=0.2, ef=0.1, dep=0.15)
        desc = "Deadline Driven"
        strategy_desc = "Focuses on urgency and due dates (55% weight on urgency)"
    else:  # smart_balance (default)
        weights = dict(u=0.35, im=0.35, ef=0.15, dep=0.15)
        desc = "Smart Balance"
        strategy_desc = "Balances all factors: urgency (35%), importance (35%), effort (15%), dependencies (15%)"

    score = (
        urgency * weights["u"]
        + importance * weights["im"]
        + effort * weights["ef"]
        + dependency * weights["dep"]
    )
    explanation = f"• Strategy: {strategy_desc}\n• Final Score: {score:.2f} (urgency: {urgency:.2f}×{weights['u']:.0%}, importance: {importance:.2f}×{weights['im']:.0%}, effort: {effort:.2f}×{weights['ef']:.0%}, dependencies: {dependency:.2f}×{weights['dep']:.0%})"
    return score, explanation


def _priority_label(score: float) -> str:
    """
    Priority labels based on combined score thresholds.
    Adjusted to better reflect high-importance tasks.
    """
    if score >= 1.0:
        return "High"
    if score >= 0.6:
        return "Medium"
    return "Low"


def analyze_tasks(raw_tasks: List[Dict[str, Any]], strategy: str, today: date | None = None):
    """
    Main entry point used by views.
    Accepts a list of validated task dicts and returns list of analyzed tasks,
    sorted by score descending.
    """
    if today is None:
        today = date.today()

    # Assign internal IDs if missing
    tasks_by_id: Dict[str, TaskData] = {}
    for idx, raw in enumerate(raw_tasks):
        tid = raw.get("id") or f"auto-{idx}"
        t = TaskData(
            id=tid,
            title=raw["title"],
            due_date=raw.get("due_date"),
            estimated_hours=float(raw.get("estimated_hours", 1.0)),
            importance=int(raw.get("importance", 5)),
            dependencies=list(raw.get("dependencies", [])),
        )
        tasks_by_id[tid] = t

    dep_scores, dep_expls, dep_warnings = _dependency_scores(tasks_by_id)

    analyzed = []
    for tid, t in tasks_by_id.items():
        warnings: List[str] = []

        u_score, u_expl = _urgency_score(t, today)
        im_score, im_expl = _importance_score(t)
        ef_score, ef_expl = _effort_score(t)
        dep_score = dep_scores.get(tid, 0.0)
        dep_expl = dep_expls.get(tid, "No dependency information.")

        score, combined_expl = _combine_scores(
            t, u_score, im_score, ef_score, dep_score, strategy
        )

        # Edge-case warnings
        if t.due_date is None:
            warnings.append("Missing due_date: treated as mildly urgent.")
        if t.estimated_hours <= 0:
            warnings.append("Non-positive estimated_hours: clamped to minimum internally.")
        if t.importance < 1 or t.importance > 10:
            warnings.append("importance out of [1,10]: clamped internally.")

        # Global warnings (e.g., cycles)
        for w in dep_warnings:
            warnings.append(w)

        analyzed.append(
            {
                "id": t.id,
                "title": t.title,
                "due_date": t.due_date,
                "estimated_hours": t.estimated_hours,
                "importance": t.importance,
                "dependencies": t.dependencies,
                "score": round(score, 3),
                "priority_label": _priority_label(score),
                "explanation": f"{u_expl}\n{im_expl}\n{ef_expl}\n{dep_expl}\n{combined_expl}",
                "warnings": list(dict.fromkeys(warnings)),  # dedupe while preserving order
            }
        )

    analyzed.sort(key=lambda x: x["score"], reverse=True)
    return analyzed


