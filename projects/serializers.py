from rest_framework import serializers
from .models import Project, Issue, Comment


class ReadCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


class WriteCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        exclude = ['issue', 'author_user']


class ReadIssueSerializer(serializers.ModelSerializer):
    comments = ReadCommentSerializer(many=True, read_only=True)

    class Meta:
        model = Issue
        fields = '__all__'


class WriteIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        exclude = ['project', 'author_user']

    def validate_assignee_user(self, value):
        if not value:
            return self.context['request'].user
        return value


class ReadProjectSerializer(serializers.ModelSerializer):
    issues = ReadIssueSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = '__all__'


class WriteProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        exclude = ['author_user_id']
