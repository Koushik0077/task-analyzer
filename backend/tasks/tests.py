from django.test import TestCase
from datetime import date, timedelta

from .scoring import analyze_tasks


class ScoringTests(TestCase):
    def test_high_importance_beats_low_importance(self):
        today = date.today()
        tasks = [
            {
                "id": "low",
                "title": "Low importance task",
                "due_date": today,
                "estimated_hours": 2,
                "importance": 3,
                "dependencies": [],
            },
            {
                "id": "high",
                "title": "High importance task",
                "due_date": today,
                "estimated_hours": 2,
                "importance": 9,
                "dependencies": [],
            },
        ]

        analyzed = analyze_tasks(tasks, strategy="high_impact", today=today)
        top = analyzed[0]["id"]
        self.assertEqual(top, "high")

    def test_overdue_task_ranked_higher(self):
        today = date.today()
        tasks = [
            {
                "id": "future",
                "title": "Future task",
                "due_date": today + timedelta(days=7),
                "estimated_hours": 2,
                "importance": 7,
                "dependencies": [],
            },
            {
                "id": "overdue",
                "title": "Overdue task",
                "due_date": today - timedelta(days=1),
                "estimated_hours": 2,
                "importance": 7,
                "dependencies": [],
            },
        ]
        analyzed = analyze_tasks(tasks, strategy="deadline_driven", today=today)
        top = analyzed[0]["id"]
        self.assertEqual(top, "overdue")

    def test_fastest_wins_prefers_low_effort(self):
        today = date.today()
        tasks = [
            {
                "id": "big",
                "title": "Big task",
                "due_date": today,
                "estimated_hours": 10,
                "importance": 7,
                "dependencies": [],
            },
            {
                "id": "small",
                "title": "Small task",
                "due_date": today,
                "estimated_hours": 1,
                "importance": 7,
                "dependencies": [],
            },
        ]
        analyzed = analyze_tasks(tasks, strategy="fastest_wins", today=today)
        top = analyzed[0]["id"]
        self.assertEqual(top, "small")

    def test_tasks_with_dependencies_get_boost(self):
        """Test that tasks with dependents receive higher scores"""
        today = date.today()
        tasks = [
            {
                "id": "blocker",
                "title": "Task that blocks others",
                "due_date": today + timedelta(days=5),
                "estimated_hours": 3,
                "importance": 5,
                "dependencies": [],
            },
            {
                "id": "isolated",
                "title": "Isolated task",
                "due_date": today + timedelta(days=5),
                "estimated_hours": 3,
                "importance": 5,
                "dependencies": [],
            },
            {
                "id": "dependent1",
                "title": "Depends on blocker",
                "due_date": today + timedelta(days=5),
                "estimated_hours": 2,
                "importance": 5,
                "dependencies": ["blocker"],
            },
            {
                "id": "dependent2",
                "title": "Also depends on blocker",
                "due_date": today + timedelta(days=5),
                "estimated_hours": 2,
                "importance": 5,
                "dependencies": ["blocker"],
            },
        ]
        analyzed = analyze_tasks(tasks, strategy="smart_balance", today=today)
        # The blocker task should rank higher due to dependency boost
        blocker_rank = next(i for i, t in enumerate(analyzed) if t["id"] == "blocker")
        isolated_rank = next(i for i, t in enumerate(analyzed) if t["id"] == "isolated")
        self.assertLess(blocker_rank, isolated_rank, "Blocker task should rank higher than isolated task")

    def test_missing_due_date_handled_gracefully(self):
        """Test that tasks without due dates are handled without errors"""
        today = date.today()
        tasks = [
            {
                "id": "no_date",
                "title": "Task without due date",
                "due_date": None,
                "estimated_hours": 2,
                "importance": 8,
                "dependencies": [],
            },
            {
                "id": "with_date",
                "title": "Task with due date",
                "due_date": today + timedelta(days=3),
                "estimated_hours": 2,
                "importance": 8,
                "dependencies": [],
            },
        ]
        # Should not raise any errors
        analyzed = analyze_tasks(tasks, strategy="smart_balance", today=today)
        self.assertEqual(len(analyzed), 2)
        # Task with due date should rank higher due to urgency
        self.assertEqual(analyzed[0]["id"], "with_date")


