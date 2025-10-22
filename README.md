# 🏦 Credit Approval System (Django REST API)

This project implements a **Credit Approval System** that allows customers to register, check loan eligibility, and apply for loans.  
It is built using **Django 4.2**, **Django REST Framework**, and **SQLite**.

---

## 🚀 Features

- Register new customers  
- Check loan eligibility using credit scoring logic  
- Create and approve/reject loans  
- View all loans for a customer  
- View details of a specific loan  
- EMI calculation included  

---

## 🧰 Tech Stack

- **Backend:** Django 4.2  
- **API Framework:** Django REST Framework  
- **Database:** SQLite  
- **Language:** Python 3.13  
- **Task Queue (Optional):** Celery + Redis  

---

## ⚙️ Setup Instructions

### 1️⃣ Clone this repository
```bash
git clone https://github.com/<your-username>/credit_approval_system.git
cd credit_approval_system

2️⃣ Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Run migrations
python manage.py makemigrations
python manage.py migrate

5️⃣ Run the development server
python manage.py runserver


Then open:
👉 http://127.0.0.1:8000/

🔗 API Endpoints

| Method | Endpoint                         | Description                  |
| ------ | -------------------------------- | ---------------------------- |
| POST   | `/api/register/`                 | Register a new customer      |
| POST   | `/api/check-eligibility/`        | Check eligibility for a loan |
| POST   | `/api/create-loan/`              | Create a loan                |
| GET    | `/api/view-loan/<loan_id>/`      | View details of a loan       |
| GET    | `/api/view-loans/<customer_id>/` | View all loans of a customer |

🧩 Sample JSON Requests
Register Customer
{
  "first_name": "Kavya",
  "last_name": "Shree",
  "age": 22,
  "phone_number": 9876543210,
  "monthly_income": 50000
}

Check Loan Eligibility
{
  "customer_id": 1,
  "loan_amount": 100000,
  "interest_rate": 10,
  "tenure": 12
}

Create Loan
{
  "customer_id": 1,
  "loan_amount": 200000,
  "interest_rate": 10,
  "tenure": 12
}

📊 Sample Responses
✅ Loan Approved
{
  "loan_id": 2,
  "customer_id": 1,
  "loan_approved": true,
  "message": "Loan approved",
  "monthly_installment": 4395.83
}

❌ Loan Rejected
{
  "loan_id": null,
  "loan_approved": false,
  "message": "Existing EMIs exceed 50% salary"
}

📎 Project Status

✅ Working API
✅ Tested using Postman
✅ Admin panel functional
✅ SQLite database ready

Developer: Kavyashree
Project: Credit Approval System — Django REST API