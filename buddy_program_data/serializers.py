from rest_framework import serializers
from buddy_program_data.models import Program_Semester, Day
from buddy_program_data.models import Volunteer_Reason, Team_Meeting_Time

class Program_Semester_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Program_Semester
        fields = "__all__"

class Day_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Day
        fields = "__all__"

class Team_Meeting_Time_Serializer(serializers.ModelSerializer):
    meeting_day = Day_Serializer(read_only=True,)
    class Meta:
        model = Team_Meeting_Time
        fields = "__all__"


class Volunteer_Reason_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Volunteer_Reason
        fields = ('name',)