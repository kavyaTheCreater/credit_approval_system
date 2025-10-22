from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

# Simple base route (optional)
def home(request):
    return JsonResponse({
        "message": "Welcome to Credit Approval System API 🎯",
        "routes": {
            "register_customer": "/api/register/",
            "check_eligibility": "/api/check-eligibility/",
            "create_loan": "/api/create-loan/",
            "view_customer_loans": "/api/view-loans/<customer_id>/",
            "view_loan": "/api/view-loan/<loan_id>/"
        }
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('loans.urls')),  # ✅ include app routes
    path('', home),                       # ✅ optional homepage
]
