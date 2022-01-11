from rest_framework import serializers

from .models import Contributor


class WriteContributorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contributor
        exclude = ['project', 'role']


class ReadContributorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contributor
        fields = ['id', 'project','user_id', 'role']
        read_only_fields = fields
