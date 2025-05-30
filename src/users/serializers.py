from rest_framework import serializers
from app.db_handler import SQLHandler
from .models import User, Company


class UserSerializer(serializers.ModelSerializer):
    """
        Register User Serializer
    """
    customer_number = serializers.IntegerField(write_only=True)

    class Meta:
        model = User
        fields = ['customer_number', 'email', 'password']

    def validate_customer_number(self, customer_number):
        result = SQLHandler().validate_customer_number(customer_number)
        if result is None:
            raise serializers.ValidationError('Número de Cliente Inválido')
        else:
            company, _ = Company.objects.get_or_create(**result)
            return company

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('El usuario con este email ya existe')
        return email

    def create(self, validated_data):
        return User.objects.create_user(
            validated_data.get('email'),
            validated_data.get('password'),
            company=validated_data.get('customer_number')
        )


class CompanyChangeSerializer(serializers.ModelSerializer):
    """Serializer for User change comapny"""

    class Meta:
        model = User
        fields = ["company"]


class CompanySerializer(serializers.ModelSerializer):
    """
        Serializer for user Companies
    """
    id = serializers.CharField(source='random_slug')
    name = serializers.CharField(source='company_name')

    class Meta:
        model = Company
        fields = ['name', 'id']
