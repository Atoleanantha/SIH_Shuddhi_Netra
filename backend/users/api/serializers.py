
from rest_framework import serializers
from users.models import User, DivisionalOffice, SubDivisionalOffice


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'is_divisional', 'is_sub_divisional']
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class DivisionalOfficeSignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    confirm_password = serializers.CharField(write_only=True, style={"input_type": "password"})

    # Fields for the `DivisionalOffice` model
    full_name = serializers.CharField(max_length=50)
    phone_number = serializers.CharField(max_length=10)
    address = serializers.CharField()
    pincode = serializers.IntegerField()

    class Meta:
        model = User
        fields = ['username', 'password', 'confirm_password', 'email', 'full_name', 'phone_number', 'address', 'pincode']

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match!"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email'],
            is_divisional=True,
        )
        DivisionalOffice.objects.create(
            user=user,
            full_name=validated_data['full_name'],
            phone_number=validated_data['phone_number'],
            email=validated_data['email'],
            address=validated_data['address'],
            pincode=validated_data['pincode'],
        )
        return user


class SubDivisionalOfficeSignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    confirm_password = serializers.CharField(write_only=True, style={"input_type": "password"})

     # Fields for the `DivisionalOffice` model
    full_name = serializers.CharField(max_length=50)
    phone_number = serializers.CharField(max_length=10)
    address = serializers.CharField()
    pincode = serializers.IntegerField()
    division_pincode = serializers.IntegerField()
    class Meta:
        model = User
        fields = [
            'username',
            'password',
            'confirm_password',
            'email',
            'full_name',
            'phone_number',
            'address',
            'pincode',
            'division_pincode',
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match!"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email'],
            is_sub_divisional=True,
        )
        SubDivisionalOffice.objects.create(
            user=user,
            full_name=validated_data['full_name'],
            phone_number=validated_data['phone_number'],
            email=validated_data['email'],
            address=validated_data['address'],
            pincode=validated_data['pincode'],
            division_pincode=validated_data['division_pincode'],
        )
        return user

class DivisionalOfficeSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username")

    class Meta:
        model = DivisionalOffice
        fields = ['username', 'full_name', 'phone_number', 'address', 'pincode']


class SubDivisionalOfficeSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username")

    class Meta:
        model = SubDivisionalOffice
        fields = ['username', 'full_name', 'phone_number', 'address', 'pincode', 'division_pincode']
