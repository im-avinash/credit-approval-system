from rest_framework import serializers
from .models import Customer

class CustomerRegisterSerializer(serializers.ModelSerializer):
    monthly_income = serializers.IntegerField(source='monthly_salary')

    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'age', 'monthly_income', 'phone_number']

    def create(self, validated_data):
        monthly_salary = validated_data['monthly_salary']
        # Calculate approved_limit: 36 * monthly_salary, rounded to nearest lakh
        limit = 36 * monthly_salary
        approved_limit = round(limit / 100000) * 100000
        
        validated_data['approved_limit'] = approved_limit
        return super().create(validated_data)

class CustomerResponseSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    monthly_income = serializers.IntegerField(source='monthly_salary')
    
    class Meta:
        model = Customer
        fields = ['id', 'name', 'age', 'monthly_income', 'approved_limit', 'phone_number']
        extra_kwargs = {'id': {'read_only': True}} 

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"