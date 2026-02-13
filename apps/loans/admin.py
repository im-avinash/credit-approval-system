from django.contrib import admin
from .models import Loan

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'loan_amount', 'interest_rate', 'tenure', 'monthly_repayment')
    list_filter = ('interest_rate', 'tenure')
    search_fields = ('customer__first_name', 'customer__phone_number')