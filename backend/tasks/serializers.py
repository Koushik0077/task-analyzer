from rest_framework import serializers


class TaskInputSerializer(serializers.Serializer):
    id = serializers.CharField(required=False, allow_blank=True)
    title = serializers.CharField(max_length=255)
    due_date = serializers.DateField(required=False, allow_null=True)
    estimated_hours = serializers.FloatField(required=False, allow_null=True, min_value=0.0)
    importance = serializers.IntegerField(required=False, allow_null=True, min_value=1, max_value=10)
    dependencies = serializers.ListField(
        child=serializers.CharField(), required=False, allow_empty=True
    )

    def validate(self, attrs):
        # Default values if missing
        if "estimated_hours" not in attrs or attrs["estimated_hours"] is None:
            attrs["estimated_hours"] = 1.0
        if "importance" not in attrs or attrs["importance"] is None:
            attrs["importance"] = 5
        if "dependencies" not in attrs or attrs["dependencies"] is None:
            attrs["dependencies"] = []

        return attrs


class AnalyzeRequestSerializer(serializers.Serializer):
    strategy = serializers.ChoiceField(
        choices=["fastest_wins", "high_impact", "deadline_driven", "smart_balance"],
        default="smart_balance",
    )
    tasks = TaskInputSerializer(many=True)


class AnalyzedTaskSerializer(serializers.Serializer):
    id = serializers.CharField(required=False, allow_blank=True)
    title = serializers.CharField()
    due_date = serializers.DateField(allow_null=True)
    estimated_hours = serializers.FloatField()
    importance = serializers.IntegerField()
    dependencies = serializers.ListField(child=serializers.CharField())
    score = serializers.FloatField()
    priority_label = serializers.CharField()
    explanation = serializers.CharField()
    warnings = serializers.ListField(
        child=serializers.CharField(), required=False, allow_empty=True
    )


class SuggestResponseSerializer(serializers.Serializer):
    strategy = serializers.CharField()
    suggested_for_date = serializers.DateField()
    tasks = AnalyzedTaskSerializer(many=True)



