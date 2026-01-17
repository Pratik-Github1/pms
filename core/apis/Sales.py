from decimal import Decimal
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.db import transaction
from django.utils import timezone
from django.db.models import Sum

from apps.models import SalesInvoice, SalesInvoiceItem


class SalesInvoiceCRUDView(APIView):
    permission_classes = [AllowAny]

    # -------------------------
    # CREATE INVOICE WITH ITEMS
    # -------------------------
    def post(self, request):
        data = request.data
        try:
            with transaction.atomic():
                # Create invoice header
                invoice = SalesInvoice.objects.create(
                    invoice_date=data.get("invoice_date", timezone.now()),
                    payment_mode=data.get("payment_mode", "CASH"),
                    customer_name=data.get("customer_name"),
                    doctor_name=data.get("doctor_name"),
                    discount=int(data.get("discount", 0)),
                    remarks=data.get("remarks"),
                )

                items = data.get("items", [])
                total_price = 0
                total_medicines = 0

                # Save all items
                for item in items:
                    qty = int(item.get("quantity", 0))
                    selling_price = Decimal(item.get("selling_price", 0))
                    mrp = Decimal(item.get("mrp", 0))
                    discount = int(item.get("discount", 0))
                    discount_price = (selling_price * discount) / 100
                    final_price = selling_price - discount_price

                    SalesInvoiceItem.objects.create(
                        sales_invoice_id=invoice.id,  # <-- use ID
                        medicine_id=item.get("medicine_id"),
                        quantity=qty,
                        mrp=mrp,
                        discount=discount,
                        discount_price=discount_price,
                        selling_price=final_price
                    )

                    total_price += final_price * qty
                    total_medicines += qty

                # Update invoice totals
                invoice.total_price = total_price
                invoice.total_medicines = total_medicines
                invoice.discount_price = (total_price * invoice.discount) / 100
                invoice.final_selling_price = total_price - invoice.discount_price
                invoice.save()

            return JsonResponse({
                "status": True,
                "message": "Sales invoice and items saved successfully",
                "data": {"id": invoice.id}
            }, status=201)

        except Exception as e:
            return JsonResponse({"status": False, "message": str(e)}, status=500)

    # -------------------------
    # GET INVOICE
    # -------------------------
    def get(self, request):
        invoice_id = request.GET.get("id")
        if not invoice_id:
            return JsonResponse({"status": False, "message": "Invoice ID required"}, status=400)

        try:
            invoice = SalesInvoice.objects.get(id=invoice_id)
            items_qs = SalesInvoiceItem.objects.filter(sales_invoice_id=invoice.id)

            items = []
            for i in items_qs:
                items.append({
                    "id": i.id,
                    "medicine_id": i.medicine_id,
                    "quantity": i.quantity,
                    "selling_price": float(i.selling_price),
                    "mrp": float(i.mrp),
                    "discount": i.discount,
                    "discount_price": float(i.discount_price)
                })

            return JsonResponse({
                "status": True,
                "data": {
                    "id": invoice.id,
                    "invoice_date": invoice.invoice_date,
                    "payment_mode": invoice.payment_mode,
                    "customer_name": invoice.customer_name,
                    "doctor_name": invoice.doctor_name,
                    "total_medicines": invoice.total_medicines,
                    "total_price": float(invoice.total_price),
                    "discount": invoice.discount,
                    "discount_price": float(invoice.discount_price),
                    "final_selling_price": float(invoice.final_selling_price),
                    "remarks": invoice.remarks,
                    "items": items
                }
            })

        except SalesInvoice.DoesNotExist:
            return JsonResponse({"status": False, "message": "Invoice not found"}, status=404)

    # -------------------------
    # UPDATE INVOICE + ITEMS
    # -------------------------
    def patch(self, request):
        data = request.data
        invoice_id = data.get("id")
        if not invoice_id:
            return JsonResponse({"status": False, "message": "Invoice ID required"}, status=400)

        try:
            with transaction.atomic():
                invoice = SalesInvoice.objects.get(id=invoice_id)

                # Update invoice fields
                fields = ["payment_mode", "customer_name", "doctor_name", "discount", "remarks", "mark_as_paid"]
                for field in fields:
                    if field in data:
                        setattr(invoice, field, data[field])
                invoice.save()

                # Update items if sent
                items = data.get("items", [])
                if items:
                    # Delete existing items
                    SalesInvoiceItem.objects.filter(sales_invoice_id=invoice.id).delete()

                    total_price = 0
                    total_medicines = 0

                    # Re-create all items
                    for item in items:
                        qty = int(item.get("quantity", 0))
                        selling_price = Decimal(item.get("selling_price", 0))
                        mrp = Decimal(item.get("mrp", 0))
                        discount = int(item.get("discount", 0))
                        discount_price = (selling_price * discount) / 100
                        final_price = selling_price - discount_price

                        SalesInvoiceItem.objects.create(
                            sales_invoice_id=invoice.id,
                            medicine_id=item.get("medicine_id"),
                            quantity=qty,
                            mrp=mrp,
                            discount=discount,
                            discount_price=discount_price,
                            selling_price=final_price
                        )

                        total_price += final_price * qty
                        total_medicines += qty

                    # Update totals
                    invoice.total_price = total_price
                    invoice.total_medicines = total_medicines
                    invoice.discount_price = (total_price * invoice.discount) / 100
                    invoice.final_selling_price = total_price - invoice.discount_price
                    invoice.save()

            return JsonResponse({"status": True, "message": "Invoice updated successfully"}, status=200)

        except SalesInvoice.DoesNotExist:
            return JsonResponse({"status": False, "message": "Invoice not found"}, status=404)
        except Exception as e:
            return JsonResponse({"status": False, "message": str(e)}, status=500)

    # -------------------------
    # DELETE INVOICE + ITEMS
    # -------------------------
    def delete(self, request):
        invoice_id = request.GET.get("id")
        if not invoice_id:
            return JsonResponse({"status": False, "message": "Invoice ID required"}, status=400)

        with transaction.atomic():
            SalesInvoiceItem.objects.filter(sales_invoice_id=invoice_id).delete()
            SalesInvoice.objects.filter(id=invoice_id).delete()

        return JsonResponse({"status": True, "message": "Invoice deleted successfully"}, status=200)


class SalesInvoiceItemCRUDView(APIView):
    permission_classes = [AllowAny]

    # -------------------------
    # ADD ITEM (STOCK OUT)
    # -------------------------
    def post(self, request):
        data = request.data

        required = ["sales_invoice_id", "medicine_id", "quantity", "selling_price", "mrp"]
        if not all(k in data for k in required):
            return JsonResponse({"status": False, "message": "Missing fields"}, status=400)

        try:
            invoice = SalesInvoice.objects.get(id=data["sales_invoice_id"])

            qty = int(data["quantity"])
            selling_price = Decimal(data["selling_price"])
            mrp = Decimal(data["mrp"])
            discount = int(data.get("discount", 0))

            discount_price = (selling_price * discount) / 100
            final_price = selling_price - discount_price

            with transaction.atomic():

                # ✅ CHECK IF ITEM ALREADY EXISTS
                item, created = SalesInvoiceItem.objects.get_or_create(
                    sales_invoice_id=invoice.id,
                    medicine_id=data["medicine_id"],
                    defaults={
                        "quantity": qty,
                        "mrp": mrp,
                        "discount": discount,
                        "discount_price": discount_price,
                        "selling_price": final_price,
                    }
                )

                # 🔁 IF EXISTS → UPDATE QUANTITY
                if not created:
                    item.quantity += qty
                    item.discount = discount
                    item.selling_price = final_price
                    item.discount_price = (final_price * discount) / 100
                    item.save()

                # 🔁 RECALCULATE INVOICE TOTALS
                items = SalesInvoiceItem.objects.filter(sales_invoice_id=invoice.id)

                total_price = sum(i.selling_price * i.quantity for i in items)
                total_medicines = sum(i.quantity for i in items)

                invoice.total_price = total_price
                invoice.total_medicines = total_medicines
                invoice.discount_price = (total_price * invoice.discount) / 100
                invoice.final_selling_price = total_price - invoice.discount_price
                invoice.save()

            return JsonResponse(
                {"status": True, "message": "Item added successfully"},
                status=201
            )

        except Exception as e:
            return JsonResponse({"status": False, "message": str(e)}, status=500)

    # -------------------------
    # DELETE ITEM (ROLLBACK STOCK)
    # -------------------------
    def delete(self, request):
        item_id = request.GET.get("id")

        if not item_id:
            return JsonResponse(
                {"status": False, "message": "Item ID required"},
                status=400
            )

        try:
            item = SalesInvoiceItem.objects.get(id=item_id)
            batch = MedicineBatch.objects.get(medicine_id=item.medicine_id)

            with transaction.atomic():
                batch.current_stock += item.quantity
                batch.save(update_fields=["current_stock"])

                item.delete()

            return JsonResponse(
                {"status": True, "message": "Item deleted successfully"},
                status=200
            )

        except SalesInvoiceItem.DoesNotExist:
            return JsonResponse(
                {"status": False, "message": "Item not found"},
                status=404
            )
        

from django.db.models import Count
from django.core.paginator import Paginator
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from apps.models import SalesInvoice, SalesInvoiceItem


class SalesInvoiceListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        page = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 10))
        search = request.GET.get("search", "").strip()

        qs = SalesInvoice.objects.all().order_by("-id")

        if search:
            qs = qs.filter(customer_name__icontains=search)

        paginator = Paginator(qs, page_size)
        page_obj = paginator.get_page(page)

        data = []
        for invoice in page_obj:
            total_items = SalesInvoiceItem.objects.filter(
                sales_invoice_id=invoice.id
            ).aggregate(
                total=Count("id")
            )["total"] or 0

            data.append({
                "id": invoice.id,
                "invoice_number": f"SI-{invoice.id}",
                "invoice_date": invoice.invoice_date.strftime("%d-%m-%Y"),
                "customer_name": invoice.customer_name or "-",
                "payment_mode": invoice.payment_mode,
                "total_amount": float(invoice.final_selling_price),
                "total_items": total_items,
            })

        return JsonResponse({
            "count": paginator.count,
            "results": {
                "data": data
            }
        })
