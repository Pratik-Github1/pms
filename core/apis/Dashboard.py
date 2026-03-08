from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.db.models import Count, Sum
from apps.models import (
    MedicineInventory, Supplier, SalesInvoice,
    PurchaseInvoice, ExpiryReturn
)


class DashboardStatsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        total_medicines = MedicineInventory.objects.filter(is_active=True).count()
        total_suppliers = Supplier.objects.filter(is_active=True).count()
        total_sales_bills = SalesInvoice.objects.count()
        total_purchase_bills = PurchaseInvoice.objects.count()

        low_stock_count = MedicineInventory.objects.filter(
            is_active=True, current_stock__lte=10, current_stock__gt=0
        ).count()

        out_of_stock_count = MedicineInventory.objects.filter(
            is_active=True, current_stock__lte=0
        ).count()

        expired_count = MedicineInventory.objects.filter(
            is_active=True, is_expired=True
        ).count()

        return JsonResponse({
            "status": True,
            "data": {
                "total_medicines": total_medicines,
                "total_suppliers": total_suppliers,
                "total_sales_bills": total_sales_bills,
                "total_purchase_bills": total_purchase_bills,
                "low_stock_count": low_stock_count,
                "out_of_stock_count": out_of_stock_count,
                "expired_count": expired_count,
            }
        })
