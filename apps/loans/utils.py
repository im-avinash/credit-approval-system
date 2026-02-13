from django.db.models import Sum
from datetime import date

def calculate_credit_score(customer):
    # Total loans taken in the past
    all_loans = customer.loans.all()
    total_loans_count = all_loans.count()
    
    if total_loans_count == 0:
        return 50  # Neutral score for new customers
    
    score = 0
    
    # 1. Past Loans paid on time (Component i)
    # We look at the percentage of EMIs paid on time across all loans
    total_emis = all_loans.aggregate(Sum('tenure'))['tenure__sum'] or 0
    emis_on_time = all_loans.aggregate(Sum('emis_paid_on_time'))['emis_paid_on_time__sum'] or 0
    
    if total_emis > 0:
        score += (emis_on_time / total_emis) * 40 # Weighted at 40 points

    # 2. Number of loans taken in past (Component ii)
    # Reward manageable debt history
    if total_loans_count > 0:
        score += 20 # Baseline for having history

    # 3. Loan activity in current year (Component iii)
    current_year = date.today().year
    loans_this_year = all_loans.filter(start_date__year=current_year).count()
    if loans_this_year > 0:
        score += 20 # Reward active but responsible users
        
    # 4. Loan approved volume (Component iv)
    # Check if the user has a high volume of credit already approved
    total_volume = all_loans.aggregate(Sum('loan_amount'))['loan_amount__sum'] or 0
    if total_volume > 0 and total_volume < customer.approved_limit:
        score += 20

    # 5. The Hard Stop (Component v)
    # If sum of current loans > approved limit, score is 0
    current_loans_sum = all_loans.aggregate(Sum('loan_amount'))['loan_amount__sum'] or 0
    if current_loans_sum > customer.approved_limit:
        return 0

    return min(int(score), 100)

def check_loan_eligibility(customer, loan_amount, interest_rate, tenure):
    credit_score = calculate_credit_score(customer)
    
    # Check current EMIs vs Salary
    current_loans = customer.loans.all() # In a real app, filter for active loans
    total_current_emis = current_loans.aggregate(Sum('monthly_repayment'))['monthly_repayment__sum'] or 0
    
    approval = False
    corrected_interest_rate = interest_rate

    # Apply Assignment Slab Logic
    if credit_score > 50:
        approval = True
    elif 50 >= credit_score > 30:
        approval = True
        if interest_rate < 12:
            corrected_interest_rate = 12
    elif 30 >= credit_score > 10:
        approval = True
        if interest_rate < 16:
            corrected_interest_rate = 16
    else:
        approval = False # Score < 10

    # Apply "50% of monthly salary" rule
    if total_current_emis > (0.5 * customer.monthly_salary):
        approval = False

    return {
        "customer_id": customer.id,
        "approval": approval,
        "interest_rate": interest_rate,
        "corrected_interest_rate": corrected_interest_rate,
        "tenure": tenure,
        "credit_score": credit_score # Added for better API transparency
    }