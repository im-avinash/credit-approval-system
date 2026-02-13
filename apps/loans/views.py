from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Loan
from apps.customers.models import Customer
from .serializers import LoanRequestSerializer, LoanViewSerializer
from .utils import check_loan_eligibility
from services.emi_calculator import calculate_emi
import datetime

class CheckEligibilityView(APIView):
    def post(self, request):
        serializer = LoanRequestSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            try:
                customer = Customer.objects.get(id=data['customer_id'])
            except Customer.DoesNotExist:
                return Response({"error": "Customer not found"}, status=404)
            
            result = check_loan_eligibility(
                customer, 
                data['loan_amount'], 
                data['interest_rate'], 
                data['tenure']
            )
            
            if result['approval']:
                result['monthly_installment'] = calculate_emi(
                    data['loan_amount'], 
                    result['corrected_interest_rate'], 
                    data['tenure']
                )
            else:
                result['monthly_installment'] = 0
                
            return Response(result)
        return Response(serializer.errors, status=400)

class CreateLoanView(APIView):
    def post(self, request):
        serializer = LoanRequestSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            try:
                customer = Customer.objects.get(id=data['customer_id'])
            except Customer.DoesNotExist:
                return Response({"error": "Customer not found"}, status=404)
            
            eligibility = check_loan_eligibility(
                customer, 
                data['loan_amount'], 
                data['interest_rate'], 
                data['tenure']
            )
            
            if eligibility['approval']:
                monthly_installment = calculate_emi(
                    data['loan_amount'], 
                    eligibility['corrected_interest_rate'], 
                    data['tenure']
                )
                
                loan = Loan.objects.create(
                    customer=customer,
                    loan_amount=data['loan_amount'],
                    interest_rate=eligibility['corrected_interest_rate'],
                    tenure=data['tenure'],
                    monthly_repayment=monthly_installment,
                    start_date=datetime.date.today(),
                    end_date=datetime.date.today() + datetime.timedelta(days=30*data['tenure'])
                )
                
                return Response({
                    "loan_id": loan.id,
                    "customer_id": customer.id,
                    "loan_approved": True,
                    "message": "Loan approved",
                    "monthly_installment": monthly_installment
                }, status=status.HTTP_201_CREATED)
            else:
                 return Response({
                    "loan_id": None,
                    "customer_id": customer.id,
                    "loan_approved": False,
                    "message": "Loan not approved",
                    "monthly_installment": 0
                }, status=200)

        return Response(serializer.errors, status=400)

class ViewLoanDetailView(APIView):
    def get(self, request, loan_id):
        try:
            loan = Loan.objects.get(id=loan_id)
            serializer = LoanViewSerializer(loan)
            return Response(serializer.data)
        except Loan.DoesNotExist:
            return Response({"error": "Loan not found"}, status=404)

class ViewLoansListView(APIView):
    def get(self, request, customer_id):
        loans = Loan.objects.filter(customer_id=customer_id)
        response_data = []
        for loan in loans:
            response_data.append({
                "loan_id": loan.id,
                "loan_amount": loan.loan_amount,
                "interest_rate": loan.interest_rate,
                "monthly_installment": loan.monthly_repayment,
                "repayments_left": loan.tenure - loan.emis_paid_on_time
            })
        return Response(response_data)