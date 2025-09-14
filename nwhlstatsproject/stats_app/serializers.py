from rest_framework import serializers
from .models import TeamPeriod, TeamDiff, ShotsPeriod, ShotsGoalDiff

class TeamPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamPeriod
        fields = '__all__'

class ShotsPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShotsPeriod
        fields = '__all__'

class TeamDiffSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamDiff
        fields = '__all__'

class ShotsGoalDiffSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShotsGoalDiff
        fields = '__all__'