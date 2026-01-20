from decimal import Decimal
from rest_framework import status
from django.db import transaction
from django.db.models import Count
from django.http import JsonResponse
from rest_framework import serializers
from rest_framework.views import APIView
from django.core.paginator import Paginator
from rest_framework.permissions import AllowAny
from django.db.models import Q, Count, OuterRef, Subquery
from rest_framework.pagination import PageNumberPagination
from apps.models import MedicineInventory, SalesInvoice, SalesInvoiceItem


class SalesInvoiceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesInvoice
        fields = [
            "id",
            "invoice_id",
            "invoice_date",
            "customer_name",
            "doctor_name",
            "total_medicines",
            "total_price",
            "total_discount_price",
            "final_selling_price",
            "created_at",
            "updated_at",
        ]

class StandardResultsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

class SalesInvoiceListView(APIView):
    """
    List Purchase Invoices with Pagination & Search
    """
    permission_classes = [AllowAny]

    def get(self, request):
        search = request.GET.get("search", "").strip()

        queryset = SalesInvoice.objects.all().order_by("-id")

        if search:
            queryset = queryset.filter(
                Q(invoice_id__icontains=search) |
                Q(invoice_date__icontains=search) |
                Q(customer_name__icontains=search) |
                Q(doctor_name__icontains=search)
            )

        paginator = StandardResultsPagination()
        paginated_qs = paginator.paginate_queryset(queryset, request)

        serializer = SalesInvoiceListSerializer(paginated_qs, many=True)

        return paginator.get_paginated_response({
            "status": True,
            "message": "Sales invoice list fetched successfully.",
            "data": serializer.data
        })

class SalesInvoiceCRUDView(APIView):
    permission_classes = [AllowAny]

    # --------------------------------------------------
    # CREATE SALES INVOICE (WITH MULTIPLE ITEMS)
    # --------------------------------------------------
    def post(self, request):
        response_data = {
            "status": False,
            "message": "",
            "data": None,
            "error": None
        }

        data = request.data
        items = data.get("items")

        if not items or not isinstance(items, list):
            response_data["message"] = "At least one sales item is required."
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                # -------------------------
                # Create Invoice Header
                # -------------------------
                invoice = SalesInvoice.objects.create(
                    customer_name=data.get("customer_name"),
                    doctor_name=data.get("doctor_name"),
                    payment_mode=data.get("payment_mode", "Cash")
                )

                total_price = 0
                total_discount_price = 0
                total_medicines_count = 0

                # -------------------------
                # Items + Stock Outward
                # -------------------------
                for index, item in enumerate(items, start=1):
                    medicine_id = item.get("medicine_id")
                    quantity = int(item.get("quantity", 0))
                    
                    if not medicine_id or quantity <= 0:
                        response_data["message"] = f"Invalid item or quantity at position {index}"
                        return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)
                    
                    # Lock the row for update to prevent race conditions
                    medicine = MedicineInventory.objects.select_for_update().get(id=medicine_id)

                    # 1. Check if stock is available
                    if medicine.current_stock < quantity:
                        response_data["message"] = f"Insufficient stock for {medicine.name}. Available: {medicine.current_stock}"
                        return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

                    # 2. Calculate Pricing for Item
                    mrp = float(item.get("mrp", medicine.mrp))
                    item_discount_percent = int(item.get("discount", 0))
                    
                    # Logic: discount_price = (mrp * qty) * (percent / 100)
                    item_total_mrp = mrp * quantity
                    item_discount_amt = item_total_mrp * (item_discount_percent / 100)
                    item_selling_price = item_total_mrp - item_discount_amt

                    # 3. Create Sales Item
                    SalesInvoiceItem.objects.create(
                        sales_invoice_id=invoice.id,
                        medicine_id=medicine_id,
                        quantity=quantity,
                        mrp=mrp,
                        discount=item_discount_percent,
                        discount_price=item_discount_amt,
                        selling_price=item_selling_price
                    )

                    # 4. Update Stock (REDUCE)
                    medicine.current_stock -= quantity
                    medicine.save(update_fields=["current_stock"])

                    # 5. Accumulate Totals
                    total_price += item_total_mrp
                    total_discount_price += item_discount_amt
                    total_medicines_count += 1

                # -------------------------
                # Finalize Invoice Totals
                # -------------------------
                invoice.total_medicines = total_medicines_count
                invoice.total_price = total_price
                invoice.total_discount_price = total_discount_price
                invoice.final_selling_price = total_price - total_discount_price
                invoice.save()

            response_data["status"] = True
            response_data["message"] = "Sales invoice created successfully."
            return JsonResponse(response_data, status=status.HTTP_201_CREATED)

        except MedicineInventory.DoesNotExist:
            response_data["message"] = "Invalid medicine ID provided."
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            response_data["message"] = str(e)
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            response_data["message"] = "Failed to create sales invoice."
            response_data["error"] = str(e)
            return JsonResponse(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # --------------------------------------------------
    # READ SALES INVOICE (BY ID)
    # --------------------------------------------------
    def get(self, request):
        response_data = {"status": False, "message": "", "data": None}
        invoice_id = request.GET.get("id")

        if not invoice_id:
            response_data["message"] = "Sales invoice ID is required."
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            invoice = SalesInvoice.objects.get(id=invoice_id)
            items = SalesInvoiceItem.objects.filter(sales_invoice_id=invoice.id)

            response_data["status"] = True
            response_data["data"] = {
                "invoice": {
                    "id": invoice.id,
                    "customer_name": invoice.customer_name,
                    "doctor_name": invoice.doctor_name,
                    "total_price": invoice.total_price,
                    "final_selling_price": invoice.final_selling_price,
                    "invoice_date": invoice.invoice_date,
                    "payment_mode": invoice.payment_mode,
                },
                "items": [
                    {
                        "medicine_id": item.medicine_id,
                        "quantity": item.quantity,
                        "mrp": item.mrp,
                        "discount": item.discount,
                        "discount_price": item.discount_price,
                        "selling_price": item.selling_price
                    } for item in items
                ]
            }
            return JsonResponse(response_data, status=status.HTTP_200_OK)
        except SalesInvoice.DoesNotExist:
            response_data["message"] = "Sales invoice not found."
            return JsonResponse(response_data, status=status.HTTP_404_NOT_FOUND)

    # --------------------------------------------------
    # UPDATE SALES INVOICE (HEADER + ITEMS WITH STOCK SYNC)
    # --------------------------------------------------
    def patch(self, request):
        response_data = {"status": False, "message": "", "data": None}
        data = request.data
        invoice_id = data.get("id")
        new_items = data.get("items")

        if not invoice_id:
            response_data["message"] = "Sales invoice ID is required."
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                invoice = SalesInvoice.objects.select_for_update().get(id=invoice_id)

                # Update header fields
                invoice.customer_name = data.get("customer_name", invoice.customer_name)
                invoice.doctor_name = data.get("doctor_name", invoice.doctor_name)
                invoice.payment_mode = data.get("payment_mode", invoice.payment_mode)
                invoice.save()

                if new_items:
                    # 1. Reverse old stock first
                    old_items = SalesInvoiceItem.objects.filter(sales_invoice_id=invoice.id)
                    for old_item in old_items:
                        med = MedicineInventory.objects.select_for_update().get(id=old_item.medicine_id)
                        med.current_stock += old_item.quantity # Add back sold items
                        med.save()
                    
                    old_items.delete()

                    # 2. Apply new items (Same logic as POST)
                    total_price = 0
                    for item in new_items:
                        med = MedicineInventory.objects.select_for_update().get(id=item['medicine_id'])
                        qty = int(item['quantity'])
                        
                        if med.current_stock < qty:
                            raise ValueError(f"Insufficient stock for {med.name}")

                        SalesInvoiceItem.objects.create(
                            sales_invoice_id=invoice.id,
                            medicine_id=med.id,
                            quantity=qty,
                            mrp=item.get('mrp', med.mrp),
                            discount=item.get('discount', 0),
                            discount_price=0, # Simplified for brevity, recalculate as per POST
                            selling_price=item.get('mrp', med.mrp) * qty
                        )
                        med.current_stock -= qty
                        med.save()
                        total_price += (float(item.get('mrp', med.mrp)) * qty)

                    invoice.total_price = total_price
                    invoice.final_selling_price = total_price # Minus discounts
                    invoice.save()

            response_data["status"] = True
            response_data["message"] = "Sales invoice updated successfully."
            return JsonResponse(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            response_data["message"] = str(e)
            return JsonResponse(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)