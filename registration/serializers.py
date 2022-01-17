from rest_framework import serializers
from registration.models import Volunteer_Registration, Student_Registration, Parent_Registration
from buddy_program_data.serializers import Program_Semester_Serializer, Team_Meeting_Time_Serializer

class Volunteer_Registration_Serializer(serializers.ModelSerializer):
    program_semester = serializers.StringRelatedField()
    gender = serializers.StringRelatedField()
    ethnicity = serializers.StringRelatedField()
    current_education_level = serializers.StringRelatedField()
    current_education_class = serializers.StringRelatedField()
    highest_education_level = serializers.StringRelatedField()
    opportunity_source = serializers.StringRelatedField()
    device_type = serializers.StringRelatedField()
    other_reasons = serializers.StringRelatedField(many=True)
    additional_interests = serializers.StringRelatedField(many=True)
    # meeting_times = serializers.StringRelatedField(many=True)

    meeting_times = Team_Meeting_Time_Serializer(read_only=True, many=True)
    class Meta:
        model = Volunteer_Registration
        fields = "__all__"




class Student_Registration_Serializer(serializers.ModelSerializer):
    # program_semester = serializers.StringRelatedField()
    gender = serializers.StringRelatedField()
    ethnicity = serializers.StringRelatedField()
    current_grade = serializers.StringRelatedField()
    school = serializers.StringRelatedField()
    primary_language = serializers.StringRelatedField()
    secondary_language = serializers.StringRelatedField()
    reading_level = serializers.StringRelatedField()
    session_device = serializers.StringRelatedField()
    # other_reasons = serializers.StringRelatedField(many=True)
    # additional_interests = serializers.StringRelatedField(many=True)
    # # meeting_times = serializers.StringRelatedField(many=True)

    # meeting_times = Team_Meeting_Time_Serializer(read_only=True, many=True)
    class Meta:
        model = Student_Registration
        fields = "__all__"

class Parent_Registration_Serializer(serializers.ModelSerializer):
    # program_semester = serializers.StringRelatedField()
    # gender = serializers.StringRelatedField()
    # ethnicity = serializers.StringRelatedField()
    # current_education_level = serializers.StringRelatedField()
    # current_education_class = serializers.StringRelatedField()
    # highest_education_level = serializers.StringRelatedField()
    # opportunity_source = serializers.StringRelatedField()
    # device_type = serializers.StringRelatedField()
    # other_reasons = serializers.StringRelatedField(many=True)
    # additional_interests = serializers.StringRelatedField(many=True)
    # # meeting_times = serializers.StringRelatedField(many=True)

    # meeting_times = Team_Meeting_Time_Serializer(read_only=True, many=True)
    class Meta:
        model = Parent_Registration
        fields = "__all__"