from celery import shared_task
import pandas as pd
from datetime import datetime
from .models import Customer, Loan


@shared_task
def load_initial_data():
    """
    Load initial customer and loan data from Excel files into the database.
    Handles missing/duplicate phone numbers safely.
    """
    try:
        # Load Excel files
        customer_df = pd.read_excel('data/customer_data.xlsx')
        loan_df = pd.read_excel('data/loan_data.xlsx')

        # Normalize column names (lowercase, trimmed)
        customer_df.columns = [c.strip().lower() for c in customer_df.columns]
        loan_df.columns = [c.strip().lower() for c in loan_df.columns]

        # ---- Load Customer Data ----
        for i, row in customer_df.iterrows():
            monthly_income = float(row.get('monthly_income', 0))
            approved_limit = round((36 * monthly_income) / 100000) * 100000

            # Handle phone numbers safely
            phone_raw = str(row.get('phone_number', '')).strip()
            if not phone_raw.isdigit() or phone_raw == "":
                # Assign a unique placeholder (e.g., 9000000000 + index)
                phone_number = 9000000000 + i
            else:
                phone_number = int(phone_raw)

            Customer.objects.update_or_create(
                customer_id=row.get('customer_id'),
                defaults={
                    'first_name': row.get('first_name', ''),
                    'last_name': row.get('last_name', ''),
                    'phone_number': phone_number,
                    'monthly_salary': monthly_income,
                    'approved_limit': approved_limit,
                    'current_debt': 0,
                    'age': int(row.get('age', 30))
                }
            )

        # ---- Load Loan Data ----
        for _, row in loan_df.iterrows():
            try:
                customer = Customer.objects.get(customer_id=row.get('customer_id'))
            except Customer.DoesNotExist:
                continue  # Skip if no matching customer

            Loan.objects.update_or_create(
                loan_id=row.get('loan_id'),
                defaults={
                    'customer': customer,
                    'loan_amount': float(row.get('loan_amount', 0)),
                    'tenure': int(row.get('tenure', 0)),
                    'interest_rate': float(row.get('interest_rate', 0)),
                    'monthly_repayment': float(row.get('monthly_repayment', 0)),
                    'emis_paid_on_time': int(row.get('emis paid on time', 0)),
                    'start_date': pd.to_datetime(row.get('start_date')).date()
                    if not pd.isna(row.get('start_date')) else datetime.today().date(),
                    'end_date': pd.to_datetime(row.get('end_date')).date()
                    if not pd.isna(row.get('end_date')) else datetime.today().date(),
                }
            )

        return "✅ Customer and loan data successfully loaded."

    except Exception as e:
        return f"❌ Error while loading data: {str(e)}"
