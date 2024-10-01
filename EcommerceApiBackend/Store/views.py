from django.shortcuts import render
from rest_framework.decorators import api_view,permission_classes 
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.views import APIView 
from rest_framework import status,viewsets
from .models import User, Product
from .serializers import UserSerializer,ProfileSerializer,ProductSeializer
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
    
    
class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()  # Blacklist the refresh token
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        

# profile view for getting and updating profile data
class ProfileView(RetrieveUpdateAPIView):
    serializer_class=ProfileSerializer
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        instance=self.get_object()
        name=request.data.get('name',None)
        if name:
            name=name.split(' ',1)
            instance.first_name=name[0].strip() or ''
            instance.last_name=name[1].strip() if len(name)>1 else ''

        # Use serializer to validate and update other fields
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()  # This will save the other fields
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductViewset(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSeializer
    def get_permissions(self):
        # Define different permissions for different actions
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [IsAuthenticated]  # Only authenticated users can get data

        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Only admins can create, update or delete
            permission_classes = [IsAdminUser]
        else:
            permission_classes = []  # No permissions by default

        return [permission() for permission in permission_classes]