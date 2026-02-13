# Credit Approval System 💳

A robust backend credit-scoring engine built with **Django**, **PostgreSQL**, and **Celery**. This system automates customer registration, credit eligibility assessment, and loan management based on historical financial data.

## 🚀 Architectural Overview
The system is fully containerized and uses a distributed task queue to handle large-scale data ingestion (10,000+ records) without blocking the main web server.



* **Django & DRF:** Core API logic and database management.
* **PostgreSQL:** Relational storage for customer and loan records.
* **Celery & Redis:** Background workers used for processing heavy Excel datasets.
* **Docker Compose:** Orchestrates all services for a "one-command" setup.
---
### 📂 Project Structure
```bash
credit-approval-system/
├── apps/
│   ├── customers/            # Handles customer registration and data ingestion
│   │   ├── management/       # Custom Django commands (e.g., ingest_data)
│   │   ├── migrations/       # Database schema history for customers
│   │   ├── admin.py          # Admin configuration to view Customers in dashboard
│   │   ├── models.py         # Customer database schema (name, salary, etc.)
│   │   ├── tasks.py          # Celery background tasks for Excel processing
│   │   ├── urls.py           # API routes for /customers/register
│   │   └── views.py          # Logic for handling customer registration requests
│   └── loans/                # Handles loan processing and credit scoring logic
│       ├── admin.py          # Admin configuration to view Loans in dashboard
│       ├── models.py         # Loan database schema (amount, interest, etc.)
│       ├── tests.py          # Unit tests for credit scoring and eligibility
│       ├── urls.py           # API routes for /check-eligibility and /create-loan
│       ├── utils.py          # The "Engine": Credit score and slab calculations
│       └── views.py          # Logic for loan viewing and creation APIs
├── config/                   # Project-level configuration
│   ├── celery.py             # Background worker configuration for Redis
│   ├── settings.py           # Global settings (DB, Redis, installed apps)
│   └── urls.py               # Main URL router for the entire project
├── services/
│   └── emi_calculator.py     # Shared logic for Compound Interest EMI math
├── customer_data.xlsx        # Raw customer data for initial system loading
├── loan_data.xlsx            # Raw loan history for initial system loading
├── Dockerfile                # Instructions to build the Python environment
├── docker-compose.yml        # Orchestrates Web, DB, Redis, and Celery services
├── manage.py                 # Django command-line utility
├── readme.md                 # Project documentation and API instructions
└── requirements.txt          # List of Python dependencies (Django, Pandas, etc.)
```
---

## 🛠️ Quick Start Instructions

### 1. Prerequisites
Ensure you have **Docker** and **Docker Compose** installed on your machine.

### 2. Download and Build the System
```bash
# Clone the repository
git clone https://github.com/im-avinash/credit-approval-system.git
cd credit-approval-system
```
Navigate to the project root and run:

```bash
# Build and start the containers
docker-compose up --build
```
### 3. Initialize the Database & Load Data
Open a new terminal window and execute these commands in order:
```bash 
# Apply database migrations
docker-compose exec web python manage.py migrate

# Create a superuser (for Admin Panel access)
docker-compose exec web python manage.py createsuperuser

# Ingest historical data from Excel files via background workers
docker-compose exec web python manage.py ingest_data
```

### 📬 API Reference (Test via Postman)
The base URL for all requests is http://127.0.0.1:8000/.

| Method | Endpoint | Description | Status Code |
| :--- | :--- | :--- | :--- |
| **POST** | `/customers/register` | Registers a new customer and calculates approved credit limit | 201 Created |
| **POST** | `/loans/check-eligibility` | Runs the credit scoring algorithm (0–100) to check feasibility | 200 OK |
| **POST** | `/loans/create-loan` | Validates eligibility and persists a new loan record | 201 Created |
| **GET** | `/loans/view-loan/<id>` | Retrieves detailed information for a specific loan | 200 OK |
| **GET** | `/loans/view-loans/<customer_id>` | Retrieves all current loans for a specific customer | 200 OK |

### 📊 Administrative Dashboard
Monitor ingested data and manage loans via the built-in Django Admin.

URL: http://127.0.0.1:8000/admin/

* **Credentials** : Use the superuser account created during setup.

### 🧪 Running Tests
To verify the credit scoring logic and API response integrity, run the automated test suite:
```bash
docker-compose exec web python manage.py test
```
### 📄 Key Business Logic Implemented
* **Approved Limit** : Calculated as $36 \times \text{monthly\\_salary}$ (rounded to the nearest lakh).
* **Credit Scoring** : Uses a weighted formula considering past EMI consistency, total loan volume, and recent activity.
* **Slab-Based Approval** :
  *  **Score > 50** : Approved.
  * **30 < Score ≤ 50** : Approved if interest rate $\ge 12\%$.
  * **10 < Score ≤ 30** : Approved if interest rate $\ge 16\%$.
  * **Score ≤ 10** : Automatic Rejection.
* **Debt-to-Income** : Rejection if total current EMIs exceed 50% of monthly income.
