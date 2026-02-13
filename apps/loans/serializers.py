from rest_framework import serializers
from .models import Loan

class LoanRequestSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.FloatField()
    interest_rate = serializers.FloatField()
    tenure = serializers.IntegerField()

class LoanViewSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()

    class Meta:
        model = Loan
        fields = ['id', 'customer', 'loan_amount', 'interest_rate', 'monthly_repayment', 'tenure']

    def get_customer(self, obj):
        return {
            "id": obj.customer.id,
            "first_name": obj.customer.first_name,
            "last_name": obj.customer.last_name,
            "phone_number": obj.customer.phone_number,
            "age": obj.customer.age
        }