from django.shortcuts import render
from rest_framework.decorators import api_view,permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.generics import RetrieveAPIView, ListAPIView, CreateAPIView
from rest_framework import status
from .serializers import UserSerializer
# Create your views here.


@api_view(['POST'])
@permission_classes([AllowAny])
def RegisterView(request):
    serialize=UserSerializer(data=request.data)
    if serialize.is_valid():
        user=serialize.save()
        # Generate JWT token
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': serialize.data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)
    else:
        return Response({"error":serialize.errors})
    
class ProfileView(RetrieveAPIView):
    pass