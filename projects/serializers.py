from rest_framework import serializers
from .models import Project, Issue, Comment


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        exclude = ['issue']


class IssueSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    class Meta:
        model = Issue
        exclude = ['project']

class ProjectSerializer(serializers.ModelSerializer):
    issues = IssueSerializer(many=True, read_only=True)
    # project = IssueSerializer()
    class Meta:
        model = Project
        fields = '__all__'