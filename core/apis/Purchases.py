from decimal import Decimal
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.db import transaction
from django.utils import timezone
from django.db.models import Sum

from apps.models import (
    PurchaseInvoice,
    PurchaseInvoiceItem,
    Supplier,
    Users,
    MedicineBatch
)
import logging

logger = logging.getLogger(__name__)


class PurchaseInvoiceCRUDView(APIView):
    permission_classes = [AllowAny]

    # -------------------------
    # CREATE
    # -------------------------
    def post(self, request):
        response_data = {"status": False, "message": "", "data": None, "error": None}
        data = request.data

        if not data.get("invoice_number") or not data.get("supplier_id"):
            response_data["message"] = "Invoice number and supplier_id are required."
            return JsonResponse(response_data, status=400)

        try:
            supplier = Supplier.objects.get(id=data["supplier_id"])

            with transaction.atomic():
                invoice = PurchaseInvoice.objects.create(
                    invoice_number=data["invoice_number"].strip(),
                    supplier=supplier,
                    invoice_date=data.get("invoice_date", timezone.now().date()),
                    payment_mode=data.get(
                        "payment_mode",
                        PurchaseInvoice.PAYMENT_MODE_CASH
                    ),
                    remarks=data.get("remarks"),
                    created_by=Users.objects.filter(
                        id=data.get("created_by")
                    ).first(),
                )

            response_data["status"] = True
            response_data["message"] = "Purchase invoice created successfully."
            response_data["data"] = {"id": invoice.id}
            return JsonResponse(response_data, status=201)

        except Supplier.DoesNotExist:
            return JsonResponse(
                {"status": False, "message": "Supplier not found"},
                status=404
            )

        except Exception as e:
            return JsonResponse(
                {"status": False, "message": str(e)},
                status=500
            )

    # -------------------------
    # GET (BY ID)
    # -------------------------
    def get(self, request):
        invoice_id = request.GET.get("id")
        if not invoice_id:
            return JsonResponse(
                {"status": False, "message": "Invoice ID required"},
                status=400
            )

        try:
            invoice = PurchaseInvoice.objects.get(id=invoice_id)
            return JsonResponse({
                "status": True,
                "message": "Invoice fetched successfully.",
                "data": {
                    "id": invoice.id,
                    "invoice_number": invoice.invoice_number,
                    "supplier_id": invoice.supplier_id,
                    "invoice_date": invoice.invoice_date,
                    "payment_mode": invoice.payment_mode,
                    "total_amount": invoice.total_amount,
                    "amount_paid": invoice.amount_paid,
                    "remarks": invoice.remarks,
                }
            }, status=200)

        except PurchaseInvoice.DoesNotExist:
            return JsonResponse(
                {"status": False, "message": "Invoice not found"},
                status=404
            )

    # -------------------------
    # UPDATE (PARTIAL)
    # -------------------------
    def patch(self, request):
        data = request.data
        invoice_id = data.get("id")

        if not invoice_id:
            return JsonResponse(
                {"status": False, "message": "Invoice ID required"},
                status=400
            )

        try:
            invoice = PurchaseInvoice.objects.get(id=invoice_id)

            allowed_fields = [
                "invoice_number",
                "invoice_date",
                "payment_mode",
                "amount_paid",
                "remarks",
            ]

            updated = False
            for field in allowed_fields:
                if field in data:
                    setattr(invoice, field, data[field])
                    updated = True

            if "supplier_id" in data:
                invoice.supplier = Supplier.objects.get(id=data["supplier_id"])
                updated = True

            if not updated:
                return JsonResponse(
                    {"status": False, "message": "No valid fields to update"},
                    status=400
                )

            invoice.save()
            return JsonResponse(
                {"status": True, "message": "Invoice updated successfully"},
                status=200
            )

        except PurchaseInvoice.DoesNotExist:
            return JsonResponse(
                {"status": False, "message": "Invoice not found"},
                status=404
            )

    # -------------------------
    # DELETE
    # -------------------------
    def delete(self, request):
        invoice_id = request.GET.get("id")
        if not invoice_id:
            return JsonResponse(
                {"status": False, "message": "Invoice ID required"},
                status=400
            )

        try:
            PurchaseInvoice.objects.get(id=invoice_id).delete()
            return JsonResponse(
                {"status": True, "message": "Invoice deleted successfully"},
                status=200
            )

        except PurchaseInvoice.DoesNotExist:
            return JsonResponse(
                {"status": False, "message": "Invoice not found"},
                status=404
            )

class PurchaseInvoiceItemCRUDView(APIView):
    permission_classes = [AllowAny]

    # -------------------------
    # CREATE (STOCK INWARD)
    # -------------------------
    def post(self, request):
        data = request.data

        required = [
            "purchase_invoice_id",
            "medicine_batch_id",
            "quantity",
            "purchase_price",
            "mrp",
            "selling_price",
        ]

        if not all(data.get(f) is not None for f in required):
            return JsonResponse(
                {"status": False, "message": "Missing required fields"},
                status=400
            )

        try:
            invoice = PurchaseInvoice.objects.get(id=data["purchase_invoice_id"])
            batch = MedicineBatch.objects.get(id=data["medicine_batch_id"])

            quantity = int(data["quantity"])
            purchase_price = Decimal(data["purchase_price"])
            line_total = purchase_price * quantity

            with transaction.atomic():
                item = PurchaseInvoiceItem.objects.create(
                    purchase_invoice=invoice,
                    medicine_batch=batch,
                    quantity=quantity,
                    purchase_price=purchase_price,
                    mrp=Decimal(data["mrp"]),
                    selling_price=Decimal(data["selling_price"]),
                    line_total=line_total,
                )

                # 🔥 STOCK INWARD
                batch.current_stock += quantity
                batch.save(update_fields=["current_stock"])

                # 🔁 Recalculate invoice total
                total = PurchaseInvoiceItem.objects.filter(
                    purchase_invoice=invoice
                ).aggregate(total=Sum("line_total"))["total"] or Decimal("0.00")

                invoice.total_amount = total
                invoice.save(update_fields=["total_amount"])

            return JsonResponse(
                {"status": True, "message": "Stock inward successful", "data": {"id": item.id}},
                status=201
            )

        except Exception as e:
            return JsonResponse(
                {"status": False, "message": str(e)},
                status=500
            )

    # -------------------------
    # UPDATE (STOCK SAFE)
    # -------------------------
    def patch(self, request):
        data = request.data
        item_id = data.get("id")

        if not item_id:
            return JsonResponse(
                {"status": False, "message": "Item ID required"},
                status=400
            )

        try:
            item = PurchaseInvoiceItem.objects.select_related(
                "medicine_batch",
                "purchase_invoice"
            ).get(id=item_id)

            batch = item.medicine_batch
            invoice = item.purchase_invoice

            old_qty = item.quantity
            new_qty = int(data.get("quantity", old_qty))
            qty_diff = new_qty - old_qty

            with transaction.atomic():
                # adjust stock
                batch.current_stock += qty_diff
                if batch.current_stock < 0:
                    raise ValueError("Stock cannot be negative")

                batch.save(update_fields=["current_stock"])

                # update prices
                if "purchase_price" in data:
                    item.purchase_price = Decimal(data["purchase_price"])
                if "mrp" in data:
                    item.mrp = Decimal(data["mrp"])
                if "selling_price" in data:
                    item.selling_price = Decimal(data["selling_price"])

                item.quantity = new_qty
                item.line_total = item.purchase_price * item.quantity
                item.save()

                # recalc invoice total
                total = PurchaseInvoiceItem.objects.filter(
                    purchase_invoice=invoice
                ).aggregate(total=Sum("line_total"))["total"] or Decimal("0.00")

                invoice.total_amount = total
                invoice.save(update_fields=["total_amount"])

            return JsonResponse(
                {"status": True, "message": "Invoice item updated successfully"},
                status=200
            )

        except PurchaseInvoiceItem.DoesNotExist:
            return JsonResponse(
                {"status": False, "message": "Item not found"},
                status=404
            )

        except Exception as e:
            return JsonResponse(
                {"status": False, "message": str(e)},
                status=500
            )

    # -------------------------
    # DELETE (ROLLBACK STOCK)
    # -------------------------
    def delete(self, request):
        item_id = request.GET.get("id")
        if not item_id:
            return JsonResponse(
                {"status": False, "message": "Item ID required"},
                status=400
            )

        try:
            item = PurchaseInvoiceItem.objects.select_related(
                "medicine_batch",
                "purchase_invoice"
            ).get(id=item_id)

            with transaction.atomic():
                batch = item.medicine_batch
                batch.current_stock -= item.quantity
                batch.save(update_fields=["current_stock"])

                invoice = item.purchase_invoice
                item.delete()

                total = PurchaseInvoiceItem.objects.filter(
                    purchase_invoice=invoice
                ).aggregate(total=Sum("line_total"))["total"] or Decimal("0.00")

                invoice.total_amount = total
                invoice.save(update_fields=["total_amount"])

            return JsonResponse(
                {"status": True, "message": "Item deleted and stock reverted"},
                status=200
            )

        except PurchaseInvoiceItem.DoesNotExist:
            return JsonResponse(
                {"status": False, "message": "Item not found"},
                status=404
            )
