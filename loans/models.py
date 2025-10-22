from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField(validators=[MinValueValidator(18), MaxValueValidator(100)])
    phone_number = models.BigIntegerField(unique=True)
    monthly_salary = models.DecimalField(max_digits=12, decimal_places=2)
    approved_limit = models.DecimalField(max_digits=12, decimal_places=2)
    current_debt = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        db_table = 'customers'
        indexes = [
            models.Index(fields=['phone_number']),
            models.Index(fields=['customer_id']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} (ID: {self.customer_id})"

    def calculate_credit_score(self):
        """Calculate credit score based on loan history."""
        from .utils import calculate_credit_score
        return calculate_credit_score(self)


class Loan(models.Model):
    loan_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='loans')
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2)
    tenure = models.IntegerField(help_text="Tenure in months")
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    monthly_repayment = models.DecimalField(max_digits=12, decimal_places=2)
    emis_paid_on_time = models.IntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        db_table = 'loans'
        indexes = [
            models.Index(fields=['customer', 'start_date']),
            models.Index(fields=['loan_id']),
        ]

    def __str__(self):
        return f"Loan {self.loan_id} - Customer {self.customer.customer_id}"

    @property
    def repayments_left(self):
        """Calculate number of EMIs left."""
        from datetime import date
        months_passed = (date.today().year - self.start_date.year) * 12 + (date.today().month - self.start_date.month)
        return max(0, self.tenure - months_passed)

    @property
    def is_active(self):
        """Check if the loan is still active."""
        from datetime import date
        return date.today() < self.end_date
