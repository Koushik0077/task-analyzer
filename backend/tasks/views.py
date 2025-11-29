from datetime import date
from typing import Any, List

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import (
    AnalyzeRequestSerializer,
    AnalyzedTaskSerializer,
    SuggestResponseSerializer,
)
from .scoring import analyze_tasks

# Simple in-memory cache to support GET /suggest/ without extra payload.
_LAST_ANALYZED: List[dict[str, Any]] | None = None
_LAST_STRATEGY: str | None = None
_LAST_DATE: date | None = None


class AnalyzeTasksView(APIView):
    """
    POST /api/tasks/analyze/
    Body:
    {
      "strategy": "smart_balance" | "fastest_wins" | "high_impact" | "deadline_driven",
      "tasks": [ { ...task fields... } ]
    }
    """

    def post(self, request, *args, **kwargs):
        global _LAST_ANALYZED, _LAST_STRATEGY, _LAST_DATE

        serializer = AnalyzeRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        strategy = data["strategy"]
        tasks = data["tasks"]

        analyzed = analyze_tasks(tasks, strategy=strategy)

        # Cache for suggest endpoint
        _LAST_ANALYZED = analyzed
        _LAST_STRATEGY = strategy
        _LAST_DATE = date.today()

        resp_serializer = AnalyzedTaskSerializer(analyzed, many=True)
        return Response(
            {
                "strategy": strategy,
                "count": len(analyzed),
                "tasks": resp_serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class SuggestTasksView(APIView):
    """
    GET /api/tasks/suggest/?limit=3

    Returns top N tasks (default 3) from the last analysis call.
    """

    def get(self, request, *args, **kwargs):
        global _LAST_ANALYZED, _LAST_STRATEGY

        limit = int(request.query_params.get("limit", 3))

        if not _LAST_ANALYZED:
            return Response(
                {
                    "detail": "No prior analysis found. Call /api/tasks/analyze/ first "
                    "or POST to this endpoint with tasks."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        today = date.today()
        tasks = list(_LAST_ANALYZED)
        strategy = _LAST_STRATEGY or "smart_balance"

        suggested = tasks[:limit]

        resp = {
            "strategy": strategy,
            "suggested_for_date": today,
            "tasks": suggested,
        }
        out = SuggestResponseSerializer(resp)
        return Response(out.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
        Optional: POST /api/tasks/suggest/
        Same payload as /analyze/, but we return only the top 3 suggestions.
        """
        serializer = AnalyzeRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        strategy = data["strategy"]
        tasks = data["tasks"]

        analyzed = analyze_tasks(tasks, strategy=strategy)
        top = analyzed[:3]

        today = date.today()
        resp = {
            "strategy": strategy,
            "suggested_for_date": today,
            "tasks": top,
        }
        out = SuggestResponseSerializer(resp)
        return Response(out.data, status=status.HTTP_200_OK)



