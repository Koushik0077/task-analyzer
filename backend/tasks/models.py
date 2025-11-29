from django.db import models


class Task(models.Model):
    """
    Optional DB model for future extensions.
    The core API in this assignment uses in-memory JSON, but
    having this model demonstrates how it could be persisted.
    """

    title = models.CharField(max_length=255)
    due_date = models.DateField(null=True, blank=True)
    estimated_hours = models.FloatField(null=True, blank=True)
    importance = models.IntegerField(null=True, blank=True)
    # For a real app we'd model dependencies as M2M, but we keep it simple here.
    raw_dependencies = models.JSONField(default=list, blank=True)

    def __str__(self) -> str:
        return self.title or f"Task {self.pk}"



