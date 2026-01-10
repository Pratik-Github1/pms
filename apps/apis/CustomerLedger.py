from decimal import Decimal
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.db import transaction

from apps.models import (
    CustomerLedgerEntry,
    Customer,
    SalesInvoice,
    Users
)
import logging

logger = logging.getLogger(__name__)


class CustomerLedgerCRUDView(APIView):
    permission_classes = [AllowAny]

    # -------------------------
    # CREATE
    # -------------------------
    def post(self, request):
        data = request.data

        required_fields = ["customer_id", "entry_type", "amount"]
        if not all(data.get(f) is not None for f in required_fields):
            return JsonResponse(
                {"status": False, "message": "Missing required fields"},
                status=400
            )

        try:
            customer = Customer.objects.get(id=data["customer_id"])
            entry_type = data["entry_type"]
            amount = Decimal(data["amount"])

            # ---- ENTRY TYPE RULES ----
            sales_invoice = None

            if entry_type == CustomerLedgerEntry.ENTRY_TYPE_SALE:
                invoice_id = data.get("sales_invoice_id")
                if not invoice_id:
                    return JsonResponse(
                        {"status": False, "message": "sales_invoice_id required for SALE entry"},
                        status=400
                    )

                sales_invoice = SalesInvoice.objects.get(id=invoice_id)

                # auto calculate due from invoice
                amount = sales_invoice.net_amount - sales_invoice.amount_paid

                if amount <= 0:
                    return JsonResponse(
                        {"status": False, "message": "No due amount for this invoice"},
                        status=400
                    )

            elif entry_type == CustomerLedgerEntry.ENTRY_TYPE_PAYMENT:
                if amount >= 0:
                    amount = amount * -1  # payment must be negative

            elif entry_type == CustomerLedgerEntry.ENTRY_TYPE_ADJUSTMENT:
                pass  # manual amount allowed

            else:
                return JsonResponse(
                    {"status": False, "message": "Invalid entry type"},
                    status=400
                )

            with transaction.atomic():
                entry = CustomerLedgerEntry.objects.create(
                    customer=customer,
                    sales_invoice=sales_invoice,
                    entry_type=entry_type,
                    amount=amount,
                    remarks=data.get("remarks"),
                    created_by=Users.objects.filter(
                        id=data.get("created_by")
                    ).first(),
                )

            return JsonResponse(
                {
                    "status": True,
                    "message": "Ledger entry created successfully",
                    "data": {"id": entry.id},
                },
                status=201
            )

        except Customer.DoesNotExist:
            return JsonResponse(
                {"status": False, "message": "Customer not found"},
                status=404
            )

        except SalesInvoice.DoesNotExist:
            return JsonResponse(
                {"status": False, "message": "Sales invoice not found"},
                status=404
            )

        except Exception as e:
            return JsonResponse(
                {"status": False, "message": str(e)},
                status=500
            )

    # -------------------------
    # READ (BY ID ONLY)
    # -------------------------
    def get(self, request):
        entry_id = request.GET.get("id")
        if not entry_id:
            return JsonResponse(
                {"status": False, "message": "Ledger entry ID required"},
                status=400
            )

        try:
            entry = CustomerLedgerEntry.objects.get(id=entry_id)

            return JsonResponse(
                {
                    "status": True,
                    "message": "Ledger entry fetched successfully",
                    "data": {
                        "id": entry.id,
                        "customer_id": entry.customer_id,
                        "sales_invoice_id": entry.sales_invoice_id,
                        "entry_type": entry.entry_type,
                        "amount": entry.amount,
                        "remarks": entry.remarks,
                        "created_at": entry.created_at,
                    },
                },
                status=200
            )

        except CustomerLedgerEntry.DoesNotExist:
            return JsonResponse(
                {"status": False, "message": "Ledger entry not found"},
                status=404
            )

    # -------------------------
    # UPDATE (PARTIAL – VERY RESTRICTED)
    # -------------------------
    def patch(self, request):
        data = request.data
        entry_id = data.get("id")

        if not entry_id:
            return JsonResponse(
                {"status": False, "message": "Ledger entry ID required"},
                status=400
            )

        try:
            entry = CustomerLedgerEntry.objects.get(id=entry_id)

            # ❗ RULE: SALE entries cannot be modified
            if entry.entry_type == CustomerLedgerEntry.ENTRY_TYPE_SALE:
                return JsonResponse(
                    {"status": False, "message": "SALE ledger entries cannot be edited"},
                    status=400
                )

            updated = False

            if "amount" in data:
                amount = Decimal(data["amount"])

                # PAYMENT must remain negative
                if entry.entry_type == CustomerLedgerEntry.ENTRY_TYPE_PAYMENT and amount > 0:
                    amount = amount * -1

                entry.amount = amount
                updated = True

            if "remarks" in data:
                entry.remarks = data["remarks"]
                updated = True

            if not updated:
                return JsonResponse(
                    {"status": False, "message": "No valid fields to update"},
                    status=400
                )

            entry.save()
            return JsonResponse(
                {"status": True, "message": "Ledger entry updated successfully"},
                status=200
            )

        except CustomerLedgerEntry.DoesNotExist:
            return JsonResponse(
                {"status": False, "message": "Ledger entry not found"},
                status=404
            )

    # -------------------------
    # DELETE (RESTRICTED)
    # -------------------------
    def delete(self, request):
        entry_id = request.GET.get("id")
        if not entry_id:
            return JsonResponse(
                {"status": False, "message": "Ledger entry ID required"},
                status=400
            )

        try:
            entry = CustomerLedgerEntry.objects.get(id=entry_id)

            # ❗ RULE: SALE entries cannot be deleted
            if entry.entry_type == CustomerLedgerEntry.ENTRY_TYPE_SALE:
                return JsonResponse(
                    {"status": False, "message": "SALE ledger entries cannot be deleted"},
                    status=400
                )

            entry.delete()
            return JsonResponse(
                {"status": True, "message": "Ledger entry deleted successfully"},
                status=200
            )

        except CustomerLedgerEntry.DoesNotExist:
            return JsonResponse(
                {"status": False, "message": "Ledger entry not found"},
                status=404
            )
