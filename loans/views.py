from datetime import date
from dateutil.relativedelta import relativedelta  # ✅ Required for month calculations
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Customer, Loan
from .serializers import CustomerSerializer, LoanSerializer
from .utils import calculate_emi


class RegisterCustomer(APIView):
    """Register a new customer with monthly income and personal details."""
    def post(self, request):
        data = request.data
        try:
            approved_limit = round((36 * int(data['monthly_income'])) / 100000) * 100000
            customer = Customer.objects.create(
                first_name=data['first_name'],
                last_name=data['last_name'],
                age=data['age'],
                phone_number=data['phone_number'],
                monthly_salary=data['monthly_income'],
                approved_limit=approved_limit,
                current_debt=0
            )
            serializer = CustomerSerializer(customer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CheckEligibility(APIView):
    """Check a customer's loan eligibility based on credit score and EMI ratio."""
    def post(self, request):
        try:
            data = request.data
            customer = get_object_or_404(Customer, pk=data['customer_id'])
            credit_score = customer.calculate_credit_score()

            loan_amount = float(data['loan_amount'])
            tenure = int(data['tenure'])
            input_interest = float(data['interest_rate'])
            monthly_emi = calculate_emi(loan_amount, input_interest, tenure)

            # Check EMI-to-salary ratio
            total_current_emi = sum(l.monthly_repayment for l in customer.loans.all() if l.is_active)
            if total_current_emi > 0.5 * float(customer.monthly_salary):
                return Response({'approval': False, 'message': 'Existing EMIs exceed 50% salary'}, status=200)

            corrected_rate = input_interest
            approval = False

            # Determine approval and corrected rate based on credit score
            if credit_score > 50:
                approval = True
            elif 30 < credit_score <= 50:
                corrected_rate = max(input_interest, 12)
                approval = True
            elif 10 < credit_score <= 30:
                corrected_rate = max(input_interest, 16)
                approval = True
            elif credit_score <= 10:
                approval = False

            # Check approved limit constraint
            active_loans_total = sum(l.loan_amount for l in customer.loans.filter(end_date__gte=date.today()))
            if active_loans_total + loan_amount > customer.approved_limit:
                approval = False
                credit_score = 0

            return Response({
                'customer_id': customer.customer_id,
                'approval': approval,
                'credit_score': credit_score,
                'requested_interest_rate': input_interest,
                'corrected_interest_rate': corrected_rate,
                'tenure': tenure,
                'monthly_installment': monthly_emi
            }, status=200)

        except Exception as e:
            return Response({'error': str(e)}, status=400)


class CreateLoan(APIView):
    """Create a new loan entry if the customer passes eligibility checks."""
    def post(self, request):
        try:
            data = request.data
            customer = get_object_or_404(Customer, pk=data['customer_id'])
            credit_score = customer.calculate_credit_score()

            loan_amount = float(data['loan_amount'])
            tenure = int(data['tenure'])
            input_interest = float(data['interest_rate'])
            monthly_emi = calculate_emi(loan_amount, input_interest, tenure)

            # Eligibility check (same as in CheckEligibility)
            total_current_emi = sum(l.monthly_repayment for l in customer.loans.all() if l.is_active)
            if total_current_emi > 0.5 * float(customer.monthly_salary):
                return Response({
                    'loan_id': None,
                    'loan_approved': False,
                    'message': 'Existing EMIs exceed 50% salary'
                }, status=200)

            if credit_score <= 10:
                return Response({
                    'loan_id': None,
                    'loan_approved': False,
                    'message': 'Credit score too low'
                }, status=200)

            # ✅ Safe calculation of end date
            start_date = date.today()
            end_date = start_date + relativedelta(months=tenure)

            loan = Loan.objects.create(
                customer=customer,
                loan_amount=loan_amount,
                tenure=tenure,
                interest_rate=input_interest,
                monthly_repayment=monthly_emi,
                start_date=start_date,
                end_date=end_date
            )

            from decimal import Decimal  # ✅ Add this import at the top

            customer.current_debt += Decimal(str(loan_amount))
            customer.save()


            #customer.current_debt += loan_amount
            #customer.save()

            return Response({
                'loan_id': loan.loan_id,
                'customer_id': customer.customer_id,
                'loan_approved': True,
                'message': 'Loan approved',
                'monthly_installment': monthly_emi
            }, status=201)

        except Exception as e:
            return Response({'error': str(e)}, status=500)


class ViewLoan(APIView):
    """View details of a specific loan by loan_id."""
    def get(self, request, loan_id):
        try:
            loan = get_object_or_404(Loan, pk=loan_id)
            serializer = LoanSerializer(loan)
            return Response(serializer.data, status=200)
        except Exception as e:
            return Response({'error': str(e)}, status=400)


class ViewCustomerLoans(APIView):
    """View all loans of a specific customer."""
    def get(self, request, customer_id):
        try:
            loans = Loan.objects.filter(customer_id=customer_id)
            response = []
            for l in loans:
                response.append({
                    'loan_id': l.loan_id,
                    'loan_amount': float(l.loan_amount),
                    'interest_rate': float(l.interest_rate),
                    'monthly_installment': float(l.monthly_repayment),
                    'repayments_left': l.repayments_left
                })
            return Response(response, status=200)
        except Exception as e:
            return Response({'error': str(e)}, status=400)
