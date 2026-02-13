from django.urls import path
from .views import CheckEligibilityView, CreateLoanView, ViewLoanDetailView, ViewLoansListView

urlpatterns = [
    path('check-eligibility/', CheckEligibilityView.as_view(), name='check-eligibility'),
    path('create-loan/', CreateLoanView.as_view(), name='create-loan'),
    path('view-loan/<int:loan_id>/', ViewLoanDetailView.as_view(), name='view-loan-detail'),
    path('view-loans/<int:customer_id>/', ViewLoansListView.as_view(), name='view-loans-list'),
]