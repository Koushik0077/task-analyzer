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


