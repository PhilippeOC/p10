from rest_framework import serializers
from users.models import User


class ReadRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'first_name', 'last_name']


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """ Inscription de l'utilisateur """
        password = validated_data.pop('password')
        instance = User(**validated_data)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
