from decimal import Decimal
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.db import transaction
from django.utils import timezone
from django.db.models import Sum

from apps.models import (
    SalesInvoice,
    SalesInvoiceItem,
    Customer,
    Users,
    MedicineBatch
)


class SalesInvoiceCRUDView(APIView):
    permission_classes = [AllowAny]

    # -------------------------
    # CREATE
    # -------------------------
    def post(self, request):
        data = request.data

        if not data.get("invoice_number"):
            return JsonResponse(
                {"status": False, "message": "Invoice number is required"},
                status=400
            )

        try:
            with transaction.atomic():
                invoice = SalesInvoice.objects.create(
                    invoice_number=data["invoice_number"].strip(),
                    invoice_date=data.get("invoice_date", timezone.now()),
                    customer=Customer.objects.filter(
                        id=data.get("customer_id")
                    ).first(),
                    status=data.get(
                        "status",
                        SalesInvoice.STATUS_COMPLETED
                    ),
                    payment_mode=data.get(
                        "payment_mode",
                        SalesInvoice.PAYMENT_MODE_CASH
                    ),
                    discount_amount=Decimal(
                        data.get("discount_amount", 0)
                    ),
                    amount_paid=Decimal(
                        data.get("amount_paid", 0)
                    ),
                    remarks=data.get("remarks"),
                    created_by=Users.objects.filter(
                        id=data.get("created_by")
                    ).first(),
                )

            return JsonResponse(
                {
                    "status": True,
                    "message": "Sales invoice created successfully",
                    "data": {"id": invoice.id},
                },
                status=201
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
            invoice = SalesInvoice.objects.get(id=invoice_id)

            return JsonResponse(
                {
                    "status": True,
                    "message": "Sales invoice fetched successfully",
                    "data": {
                        "id": invoice.id,
                        "invoice_number": invoice.invoice_number,
                        "invoice_date": invoice.invoice_date,
                        "customer_id": invoice.customer_id,
                        "status": invoice.status,
                        "payment_mode": invoice.payment_mode,
                        "total_amount": invoice.total_amount,
                        "discount_amount": invoice.discount_amount,
                        "net_amount": invoice.net_amount,
                        "amount_paid": invoice.amount_paid,
                        "remarks": invoice.remarks,
                    },
                },
                status=200
            )

        except SalesInvoice.DoesNotExist:
            return JsonResponse(
                {"status": False, "message": "Invoice not found"},
                status=404
            )

    # -------------------------
    # UPDATE (PARTIAL – HEADER ONLY)
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
            invoice = SalesInvoice.objects.get(id=invoice_id)

            allowed_fields = [
                "invoice_date",
                "status",
                "payment_mode",
                "discount_amount",
                "amount_paid",
                "remarks",
            ]

            updated = False
            for field in allowed_fields:
                if field in data:
                    setattr(invoice, field, data[field])
                    updated = True

            if "customer_id" in data:
                invoice.customer = Customer.objects.filter(
                    id=data["customer_id"]
                ).first()
                updated = True

            if not updated:
                return JsonResponse(
                    {"status": False, "message": "No valid fields to update"},
                    status=400
                )

            # net_amount recalculation
            invoice.net_amount = (
                invoice.total_amount - invoice.discount_amount
            )

            invoice.save()

            return JsonResponse(
                {"status": True, "message": "Sales invoice updated successfully"},
                status=200
            )

        except SalesInvoice.DoesNotExist:
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
            SalesInvoice.objects.get(id=invoice_id).delete()
            return JsonResponse(
                {"status": True, "message": "Sales invoice deleted"},
                status=200
            )

        except SalesInvoice.DoesNotExist:
            return JsonResponse(
                {"status": False, "message": "Invoice not found"},
                status=404
            )

class SalesInvoiceItemCRUDView(APIView):
    permission_classes = [AllowAny]

    # -------------------------
    # CREATE (STOCK OUTWARD)
    # -------------------------
    def post(self, request):
        data = request.data

        required = [
            "sales_invoice_id",
            "medicine_batch_id",
            "quantity",
            "selling_price",
            "mrp",
        ]

        if not all(data.get(f) is not None for f in required):
            return JsonResponse(
                {"status": False, "message": "Missing required fields"},
                status=400
            )

        try:
            invoice = SalesInvoice.objects.get(id=data["sales_invoice_id"])
            batch = MedicineBatch.objects.get(id=data["medicine_batch_id"])

            quantity = int(data["quantity"])

            if batch.current_stock < quantity:
                return JsonResponse(
                    {"status": False, "message": "Insufficient stock"},
                    status=400
                )

            selling_price = Decimal(data["selling_price"])
            line_total = selling_price * quantity

            with transaction.atomic():
                item = SalesInvoiceItem.objects.create(
                    sales_invoice=invoice,
                    medicine_batch=batch,
                    quantity=quantity,
                    selling_price=selling_price,
                    mrp=Decimal(data["mrp"]),
                    line_total=line_total,
                )

                # 🔻 STOCK OUTWARD
                batch.current_stock -= quantity
                batch.save(update_fields=["current_stock"])

                # 🔁 Recalculate totals
                total = SalesInvoiceItem.objects.filter(
                    sales_invoice=invoice
                ).aggregate(total=Sum("line_total"))["total"] or Decimal("0.00")

                invoice.total_amount = total
                invoice.net_amount = (
                    total - invoice.discount_amount
                )
                invoice.save(update_fields=["total_amount", "net_amount"])

            return JsonResponse(
                {
                    "status": True,
                    "message": "Stock outward successful",
                    "data": {"id": item.id},
                },
                status=201
            )

        except SalesInvoice.DoesNotExist:
            return JsonResponse(
                {"status": False, "message": "Invoice not found"},
                status=404
            )

        except MedicineBatch.DoesNotExist:
            return JsonResponse(
                {"status": False, "message": "Medicine batch not found"},
                status=404
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
            item = SalesInvoiceItem.objects.select_related(
                "medicine_batch",
                "sales_invoice"
            ).get(id=item_id)

            batch = item.medicine_batch
            invoice = item.sales_invoice

            old_qty = item.quantity
            new_qty = int(data.get("quantity", old_qty))
            qty_diff = new_qty - old_qty

            # qty_diff > 0 → more stock needed
            if qty_diff > 0 and batch.current_stock < qty_diff:
                return JsonResponse(
                    {"status": False, "message": "Insufficient stock"},
                    status=400
                )

            with transaction.atomic():
                # adjust stock
                batch.current_stock -= qty_diff
                batch.save(update_fields=["current_stock"])

                if "selling_price" in data:
                    item.selling_price = Decimal(data["selling_price"])
                if "mrp" in data:
                    item.mrp = Decimal(data["mrp"])

                item.quantity = new_qty
                item.line_total = item.selling_price * item.quantity
                item.save()

                # recalc invoice totals
                total = SalesInvoiceItem.objects.filter(
                    sales_invoice=invoice
                ).aggregate(total=Sum("line_total"))["total"] or Decimal("0.00")

                invoice.total_amount = total
                invoice.net_amount = (
                    total - invoice.discount_amount
                )
                invoice.save(update_fields=["total_amount", "net_amount"])

            return JsonResponse(
                {"status": True, "message": "Sales item updated successfully"},
                status=200
            )

        except SalesInvoiceItem.DoesNotExist:
            return JsonResponse(
                {"status": False, "message": "Item not found"},
                status=404
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
            item = SalesInvoiceItem.objects.select_related(
                "medicine_batch",
                "sales_invoice"
            ).get(id=item_id)

            with transaction.atomic():
                # rollback stock
                batch = item.medicine_batch
                batch.current_stock += item.quantity
                batch.save(update_fields=["current_stock"])

                invoice = item.sales_invoice
                item.delete()

                total = SalesInvoiceItem.objects.filter(
                    sales_invoice=invoice
                ).aggregate(total=Sum("line_total"))["total"] or Decimal("0.00")

                invoice.total_amount = total
                invoice.net_amount = (
                    total - invoice.discount_amount
                )
                invoice.save(update_fields=["total_amount", "net_amount"])

            return JsonResponse(
                {"status": True, "message": "Item deleted and stock reverted"},
                status=200
            )

        except SalesInvoiceItem.DoesNotExist:
            return JsonResponse(
                {"status": False, "message": "Item not found"},
                status=404
            )
