from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from users.serializers import RegistrationSerializer, ReadRegistrationSerializer
from users.permissions import SignupPermissions
from users.models import User


class UserCreate(APIView):
    permission_classes = [SignupPermissions]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            account = serializer.save()
            refresh = RefreshToken.for_user(account)
            data = {'registration': 'Inscription réussie !',
                    'last_name': account.last_name,
                    'first_name': account.first_name,
                    'email': account.email,
                    'token': {
                                'refresh': str(refresh),
                                'access': str(refresh.access_token),
                             }
                    }
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        users = User.objects.all()
        serializer = ReadRegistrationSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
