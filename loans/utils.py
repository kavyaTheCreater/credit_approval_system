import math
from datetime import date
from dateutil.relativedelta import relativedelta
from .models import Loan


def calculate_emi(principal, annual_rate, months):
    """Calculate EMI using compound interest formula."""
    monthly_rate = annual_rate / (12 * 100)
    if monthly_rate == 0:
        return round(principal / months, 2)
    emi = principal * monthly_rate * ((1 + monthly_rate) ** months) / ((1 + monthly_rate) ** months - 1)
    return round(emi, 2)


def calculate_credit_score(customer):
    """Calculate credit score (0–100) based on historical loans."""
    loans = Loan.objects.filter(customer=customer)

    # No previous loans = perfect score
    if not loans.exists():
        return 100

    score = 50

    # i. Past loans paid on time
    total_emis = sum(l.tenure for l in loans)
    paid_on_time = sum(l.emis_paid_on_time for l in loans)
    on_time_ratio = (paid_on_time / total_emis) if total_emis > 0 else 1
    if on_time_ratio > 0.9:
        score += 30
    elif on_time_ratio > 0.7:
        score += 15
    elif on_time_ratio < 0.5:
        score -= 10

    # ii. Number of loans taken
    if loans.count() > 10:
        score -= 10
    elif loans.count() > 5:
        score -= 5

    # iii. Loan activity in current year
    if loans.filter(start_date__year=date.today().year).exists():
        score += 10

    # iv. Loan approved volume
    total_loan_volume = sum(l.loan_amount for l in loans)
    if total_loan_volume > (customer.approved_limit * 5):
        score -= 10

    # v. Debt vs approved limit
    total_active_debt = sum(l.loan_amount for l in loans if l.is_active)
    if total_active_debt > customer.approved_limit:
        return 0

    # Clamp the score between 0–100
    score = max(0, min(100, score))
    return score
