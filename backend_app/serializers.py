from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer, GeometryField
from django.contrib.auth.password_validation import validate_password

from .models import User, UserLine


class UserSerializer(serializers.ModelSerializer):
    email = serializers.CharField(required=True)
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    home_office_distance = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'password2', 'email', 'country', 'bio', 'phone_number',
                  'birthday', 'areas_of_interest', 'home_address', 'office_address', 'age', 'home_office_distance']

    def get_home_office_distance(self, obj):
        return obj.get_home_office_distance()

    def validate(self, attrs):
        password2 = attrs.pop('password2')
        if attrs['password'] != password2:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        areas_of_interest = validated_data.pop('areas_of_interest')
        print(validated_data)
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        user.areas_of_interest.set(areas_of_interest)

        return user


class UserLineSerializer(GeoFeatureModelSerializer):
    user = UserSerializer()

    class Meta:
        model = UserLine
        geo_field = 'line'
        fields = ['line', 'user']


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])

    class Meta:
        fields = ['username', 'password']
