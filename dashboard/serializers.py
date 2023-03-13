from rest_framework import serializers

from information.models import Education, Competence, Experience, Information, Project

class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = "__all__"


class CompetenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competence
        fields = "__all__"



class ExperienceSerializer(serializers.ModelSerializer):
    stack = CompetenceSerializer(many=True, required=False, allow_null=True)
    class Meta:
        model = Experience
        fields = "__all__"




class InformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Information
        fields = "__all__"

class ProjectSerializer(serializers.ModelSerializer):
    tools = CompetenceSerializer(many=True, required=False, allow_null=True)
    class Meta:
        model = Project
        fields = "__all__"