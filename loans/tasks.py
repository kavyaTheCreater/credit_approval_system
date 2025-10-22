from celery import shared_task
import pandas as pd
from datetime import datetime
from .models import Customer, Loan


@shared_task
def load_initial_data():
    """Load initial customer and loan data from Excel into the database."""
    customer_df = pd.read_excel('data/customer_data.xlsx')
    loan_df = pd.read_excel('data/loan_data.xlsx')

    # Load customers
    for _, row in customer_df.iterrows():
        Customer.objects.update_or_create(
            customer_id=row['customer_id'],
            defaults={
                'first_name': row['first_name'],
                'last_name': row['last_name'],
                'phone_number': row['phone_number'],
                'monthly_salary': row['monthly_salary'],
                'approved_limit': row['approved_limit'],
                'current_debt': row['current_debt'],
                'age': int(row.get('age', 30)) if 'age' in row else 30
            }
        )

    # Load loans
    for _, row in loan_df.iterrows():
        try:
            customer = Customer.objects.get(customer_id=row['customer_id'])
        except Customer.DoesNotExist:
            continue

        Loan.objects.update_or_create(
            loan_id=row['loan_id'],
            defaults={
                'customer': customer,
                'loan_amount': row['loan_amount'],
                'tenure': row['tenure'],
                'interest_rate': row['interest_rate'],
                'monthly_repayment': row['monthly_repayment'],
                'emis_paid_on_time': row['EMIs paid on time'],
                'start_date': pd.to_datetime(row['start_date']).date(),
                'end_date': pd.to_datetime(row['end_date']).date(),
            }
        )

    return "Customer and loan data successfully loaded."
