from celery import shared_task
import pandas as pd
from apps.customers.models import Customer
from apps.loans.models import Loan
import datetime

@shared_task
def ingest_customer_data(file_path):
    try:
        # Read the file (Handle both xlsx and csv based on extension)
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        # Iterate and save
        for _, row in df.iterrows():
            Customer.objects.update_or_create(
                id=row['Customer ID'], # Explicitly map ID to maintain relationship
                defaults={
                    'first_name': row['First Name'],
                    'last_name': row['Last Name'],
                    'age': row['Age'],
                    'phone_number': row['Phone Number'],
                    'monthly_salary': row['Monthly Salary'],
                    'approved_limit': row['Approved Limit'],
                    'current_debt': 0  # Initial default
                }
            )
        return "Customer Data Ingested Successfully"
    except Exception as e:
        return f"Error ingesting customers: {str(e)}"

@shared_task
def ingest_loan_data(file_path):
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
            
        for _, row in df.iterrows():
            customer_id = row['Customer ID']
            try:
                customer = Customer.objects.get(id=customer_id)
                
                # Update customer debt while we are here
                # (Optional optimization, or can be done dynamically)
                # customer.current_debt += row['Loan Amount'] 
                # customer.save()

                Loan.objects.update_or_create(
                    id=row['Loan ID'],
                    defaults={
                        'customer': customer,
                        'loan_amount': row['Loan Amount'],
                        'tenure': row['Tenure'],
                        'interest_rate': row['Interest Rate'],
                        'monthly_repayment': row['Monthly payment'],
                        'emis_paid_on_time': row['EMIs paid on Time'],
                        'start_date': pd.to_datetime(row['Date of Approval']).date(),
                        'end_date': pd.to_datetime(row['End Date']).date()
                    }
                )
            except Customer.DoesNotExist:
                print(f"Skipping loan {row['Loan ID']}: Customer {customer_id} not found.")
                
        return "Loan Data Ingested Successfully"
    except Exception as e:
        return f"Error ingesting loans: {str(e)}"