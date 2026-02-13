from django.db import models
from apps.customers.models import Customer  # Import instead of redefine

class Loan(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="loans")
    loan_amount = models.FloatField()
    tenure = models.IntegerField()
    interest_rate = models.FloatField()
    monthly_repayment = models.FloatField()
    emis_paid_on_time = models.IntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"Loan {self.id}"