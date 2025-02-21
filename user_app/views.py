from django.shortcuts import render
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.response import Response

from user_app.api.serializers import RegistrationSerializer
from user_app import models


@api_view(['POST'])
def logout_view(request):
    if request.method == 'POST':
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
def registration_view(request):
    if request.method == 'POST':
        serializer = RegistrationSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            user = serializer.save()
            data['response'] = "Registration successful"
            data['username'] = user.username
            data['email'] = user.email
            token = Token.objects.get(user=user)
            data['token'] = token.key
        else:
            data = serializer.errors

        return Response(data, status=status.HTTP_201_CREATED)
