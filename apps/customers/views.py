from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CustomerRegisterSerializer, CustomerResponseSerializer

class RegisterView(APIView):
    def post(self, request):
        serializer = CustomerRegisterSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save()
            response_serializer = CustomerResponseSerializer(customer)
            data = response_serializer.data
            data['customer_id'] = data.pop('id')
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)