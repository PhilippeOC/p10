from django.shortcuts import render

# from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from users.serializers import RegistrationSerializer


# @api_view(['POST'])
# def registration_view(request):
#     if request.method == 'POST':
#         serializer = RegistrationSerializer(data=request.data)
#         print('***serializer***', serializer)
#         data = {}
#         if serializer.is_valid():
#             account = serializer.save()
#             data['registration'] = 'Inscription réussie !'
#             data['last_name'] = account.last_name
#             data['first_name'] = account.first_name
#             data['email'] = account.email
#             refresh = RefreshToken.for_user(account)
#             data['token'] = {
#                                 'refresh': str(refresh),
#                                 'access': str(refresh.access_token),
#                             }
#         else:
#             data = serializer.errors
#         return Response(data)


class UserCreate(APIView):
    permission_classes = [permissions.AllowAny]
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


