from django.contrib.auth import get_user_model, login
from django.http import Http404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import permissions
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.gis.measure import D
from django.contrib.gis.geos import Point

from .models import UserLine
from .serializers import UserSerializer, UserLineSerializer, LoginSerializer

User = get_user_model()


# Create your views here.

class UserListView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_object(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, user_id):
        user = self.get_object(user_id)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def put(self, request, user_id):
        user = self.get_object(user_id)
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': 'User updated successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, user_id):
        user = self.get_object(user_id)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': 'User updated successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id):
        user = self.get_object(user_id)
        user.delete()
        return Response({'success': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


class UserLineDetailView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_object(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, user_id):
        user_line = UserLine.objects.get(user=self.get_object(user_id))
        serializer = UserLineSerializer(user_line)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SignupAPI(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = {
            "status": status.HTTP_201_CREATED,
            "message": "Singed up successfully.",
            "data": serializer.data
        }
        return Response(response, status=status.HTTP_201_CREATED)


class LoginAPI(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(request, **serializer.validated_data)
        if user is not None:
            login(request, user)
            """We are reterving the token for authenticated user."""
            token = Token.objects.get(user=user)
            response = {
                "status": status.HTTP_200_OK,
                "message": "Logged in successfully.",
                "token": token.key
            }
            return Response(response, status=status.HTTP_200_OK)
        response = {
            "status": status.HTTP_401_UNAUTHORIZED,
            "message": "Invalid username or password",
        }
        return Response(response, status=status.HTTP_401_UNAUTHORIZED)


class NearbyUserView(APIView):
    def get(self, request):
        lat = request.query_params.get('lat')
        lon = request.query_params.get('lon')

        if not (lat and lon):
            return Response({'error': 'Latitude and longitude are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_point = Point(float(lon), float(lat))
        except ValueError:
            return Response({'error': 'Invalid coordinates'}, status=status.HTTP_400_BAD_REQUEST)

        nearby_users = User.objects.filter(
            home_address__distance_lte=(user_point, D(km=10)))
        if nearby_users:
            serializer = UserSerializer(nearby_users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"message": "No users found nearby!"}, status=status.HTTP_200_OK)
