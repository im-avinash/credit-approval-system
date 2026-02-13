from django.core.management.base import BaseCommand
from apps.customers.tasks import ingest_customer_data, ingest_loan_data
import os

class Command(BaseCommand):
    help = 'Ingest initial data from Excel/CSV files'

    def handle(self, *args, **kwargs):
        # Assuming files are in the root or a 'data' folder
        customer_file = 'customer_data.xlsx' 
        loan_file = 'loan_data.xlsx'
        
        # Trigger Celery Tasks
        self.stdout.write("Starting Customer Ingestion...")
        ingest_customer_data.delay(customer_file)
        
        self.stdout.write("Starting Loan Ingestion...")
        ingest_loan_data.delay(loan_file)
        
        self.stdout.write(self.style.SUCCESS('Ingestion tasks have been queued!'))