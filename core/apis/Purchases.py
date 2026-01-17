from rest_framework import status
from django.db import transaction
from django.http import JsonResponse
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Count, OuterRef, Subquery

from apps.models import (
    Supplier,
    PurchaseInvoice,
    PurchaseInvoiceItem,
    MedicineInventory,
)

import logging
logger = logging.getLogger(__name__)


class PurchaseInvoiceCRUDView(APIView):
    permission_classes = [AllowAny]

    # --------------------------------------------------
    # CREATE PURCHASE INVOICE (WITH MULTIPLE ITEMS)
    # --------------------------------------------------
    def post(self, request):
        response_data = {
            "status": False,
            "message": "",
            "data": None,
            "error": None
        }

        data = request.data

        supplier_id = data.get("supplier_id")
        invoice_number = data.get("invoice_number")
        invoice_date = data.get("invoice_date")
        items = data.get("items")

        if not supplier_id or not invoice_number or not invoice_date:
            response_data["message"] = "Supplier ID, invoice number and invoice date are required."
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        if not items or not isinstance(items, list):
            response_data["message"] = "At least one purchase item is required."
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        if not Supplier.objects.filter(id=supplier_id).exists():
            response_data["message"] = "Invalid supplier ID."
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():

                # -------------------------
                # Create Invoice Header
                # -------------------------
                invoice = PurchaseInvoice.objects.create(
                    supplier_id=supplier_id,
                    invoice_number=invoice_number,
                    invoice_date=invoice_date,
                    payment_mode=data.get("payment_mode", "Cash"),
                    amount_paid=data.get("amount_paid", 0),
                    remarks=data.get("remarks"),
                )

                total_amount = 0

                # -------------------------
                # Items + Stock Inward
                # -------------------------
                for index, item in enumerate(items, start=1):
                    medicine_id = item.get("medicine_id")
                    quantity = item.get("quantity")
                    purchase_price = item.get("purchase_price")
                    mrp = item.get("mrp")

                    if not medicine_id or not quantity:
                        raise ValueError(f"Invalid item at position {index}")

                    medicine = MedicineInventory.objects.select_for_update().get(id=medicine_id)

                    PurchaseInvoiceItem.objects.create(
                        purchase_invoice_id=invoice.id,
                        medicine_id=medicine_id,
                        quantity=quantity,
                        purchase_price=purchase_price,
                        mrp=mrp,
                    )

                    # Stock Inward
                    medicine.current_stock += int(quantity)

                    if purchase_price is not None:
                        medicine.purchase_price = purchase_price
                    if mrp is not None:
                        medicine.mrp = mrp

                    medicine.save(update_fields=[
                        "current_stock", "purchase_price", "mrp"
                    ])

                    if purchase_price:
                        total_amount += int(quantity) * float(purchase_price)

                invoice.total_amount = total_amount
                invoice.save(update_fields=["total_amount"])

            response_data["status"] = True
            response_data["message"] = "Purchase invoice created successfully."
            response_data["data"] = {
                "invoice_id": invoice.id,
                "total_amount": str(total_amount)
            }
            return JsonResponse(response_data, status=status.HTTP_201_CREATED)

        except MedicineInventory.DoesNotExist:
            response_data["message"] = "Invalid medicine ID provided."
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.exception("Purchase Invoice Creation Failed")
            response_data["message"] = "Failed to create purchase invoice."
            response_data["error"] = str(e)
            return JsonResponse(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # --------------------------------------------------
    # READ PURCHASE INVOICE (BY ID)
    # --------------------------------------------------
    def get(self, request):
        response_data = {
            "status": False,
            "message": "",
            "data": None,
            "error": None
        }

        invoice_id = request.GET.get("id")

        if not invoice_id:
            response_data["message"] = "Purchase invoice ID is required."
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            invoice = PurchaseInvoice.objects.get(id=invoice_id)
            items = PurchaseInvoiceItem.objects.filter(
                purchase_invoice_id=invoice.id
            )

            response_data["status"] = True
            response_data["message"] = "Purchase invoice fetched successfully."
            response_data["data"] = {
                "invoice": {
                    "id": invoice.id,
                    "supplier_id": invoice.supplier_id,
                    "invoice_number": invoice.invoice_number,
                    "invoice_date": invoice.invoice_date,
                    "payment_mode": invoice.payment_mode,
                    "total_amount": invoice.total_amount,
                    "amount_paid": invoice.amount_paid,
                    "remarks": invoice.remarks,
                    "created_at": invoice.created_at,
                },
                "items": [
                    {
                        "medicine_id": item.medicine_id,
                        "quantity": item.quantity,
                        "purchase_price": item.purchase_price,
                        "mrp": item.mrp,
                    }
                    for item in items
                ]
            }

            return JsonResponse(response_data, status=status.HTTP_200_OK)

        except PurchaseInvoice.DoesNotExist:
            response_data["message"] = "Purchase invoice not found."
            return JsonResponse(response_data, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            response_data["message"] = "Failed to fetch purchase invoice."
            response_data["error"] = str(e)
            return JsonResponse(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # --------------------------------------------------
    # UPDATE PURCHASE INVOICE (HEADER + ITEMS WITH DELTA STOCK)
    # --------------------------------------------------
    def patch(self, request):
        response_data = {
            "status": False,
            "message": "",
            "data": None,
            "error": None
        }

        data = request.data
        invoice_id = data.get("id")
        new_items = data.get("items")

        if not invoice_id:
            response_data["message"] = "Purchase invoice ID is required."
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():

                invoice = PurchaseInvoice.objects.select_for_update().get(id=invoice_id)

                # -------------------------
                # Update Invoice Header
                # -------------------------
                allowed_fields = [
                    "invoice_number",
                    "invoice_date",
                    "payment_mode",
                    "amount_paid",
                    "remarks",
                ]

                for field in allowed_fields:
                    if field in data:
                        setattr(invoice, field, data.get(field))

                invoice.save()

                # -------------------------
                # If items not provided, stop here
                # -------------------------
                if not new_items:
                    response_data["status"] = True
                    response_data["message"] = "Purchase invoice updated successfully."
                    return JsonResponse(response_data, status=status.HTTP_200_OK)

                # -------------------------
                # Fetch Old Items
                # -------------------------
                old_items = PurchaseInvoiceItem.objects.filter(
                    purchase_invoice_id=invoice.id
                )

                old_item_map = {
                    item.medicine_id: item
                    for item in old_items
                }

                new_item_map = {
                    item["medicine_id"]: item
                    for item in new_items
                }

                # -------------------------
                # Reverse OLD stock
                # -------------------------
                for medicine_id, old_item in old_item_map.items():
                    medicine = MedicineInventory.objects.select_for_update().get(
                        id=medicine_id
                    )
                    medicine.current_stock -= old_item.quantity
                    medicine.save(update_fields=["current_stock"])

                # -------------------------
                # Delete old items
                # -------------------------
                old_items.delete()

                total_amount = 0

                # -------------------------
                # Apply NEW items + stock
                # -------------------------
                for index, item in enumerate(new_items, start=1):
                    medicine_id = item.get("medicine_id")
                    quantity = item.get("quantity")
                    purchase_price = item.get("purchase_price")
                    mrp = item.get("mrp")

                    if not medicine_id or not quantity:
                        raise ValueError(f"Invalid item at position {index}")

                    medicine = MedicineInventory.objects.select_for_update().get(
                        id=medicine_id
                    )

                    PurchaseInvoiceItem.objects.create(
                        purchase_invoice_id=invoice.id,
                        medicine_id=medicine_id,
                        quantity=quantity,
                        purchase_price=purchase_price,
                        mrp=mrp,
                    )

                    # Apply new stock
                    medicine.current_stock += int(quantity)

                    if purchase_price is not None:
                        medicine.purchase_price = purchase_price
                    if mrp is not None:
                        medicine.mrp = mrp

                    medicine.save(update_fields=[
                        "current_stock", "purchase_price", "mrp"
                    ])

                    if purchase_price:
                        total_amount += int(quantity) * float(purchase_price)

                invoice.total_amount = total_amount
                invoice.save(update_fields=["total_amount"])

            response_data["status"] = True
            response_data["message"] = "Purchase invoice updated successfully."
            return JsonResponse(response_data, status=status.HTTP_200_OK)

        except PurchaseInvoice.DoesNotExist:
            response_data["message"] = "Purchase invoice not found."
            return JsonResponse(response_data, status=status.HTTP_404_NOT_FOUND)

        except MedicineInventory.DoesNotExist:
            response_data["message"] = "Invalid medicine ID provided."
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.exception("Purchase Invoice Update Failed")
            response_data["message"] = "Failed to update purchase invoice."
            response_data["error"] = str(e)
            return JsonResponse(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PurchaseInvoiceListSerializer(serializers.ModelSerializer):
    supplier_company_name = serializers.CharField(read_only=True)
    total_items = serializers.IntegerField(read_only=True)

    class Meta:
        model = PurchaseInvoice
        fields = [
            "id",
            "supplier_id",
            "supplier_company_name",
            "invoice_number",
            "invoice_date",
            "payment_mode",
            "total_amount",
            "amount_paid",
            "total_items",
            "remarks",
            "created_at",
        ]


class StandardResultsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

class PurchaseInvoiceListView(APIView):
    """
    List Purchase Invoices with Pagination & Search
    """
    permission_classes = [AllowAny]

    def get(self, request):
        search = request.GET.get("search", "").strip()

        supplier_company_subquery = Supplier.objects.filter(
            id=OuterRef("supplier_id")
        ).values("company_name")[:1]

        queryset = (
            PurchaseInvoice.objects
            .annotate(
                supplier_company_name=Subquery(supplier_company_subquery),
                total_items=Count("id", filter=Q(
                    id__in=PurchaseInvoiceItem.objects.values("purchase_invoice_id")
                ))
            )
            .order_by("-id")
        )

        if search:
            queryset = queryset.filter(
                Q(invoice_number__icontains=search) |
                Q(payment_mode__icontains=search) |
                Q(remarks__icontains=search) |
                Q(supplier_company_name__icontains=search)
            )

        paginator = StandardResultsPagination()
        paginated_qs = paginator.paginate_queryset(queryset, request)

        serializer = PurchaseInvoiceListSerializer(paginated_qs, many=True)

        return paginator.get_paginated_response({
            "status": True,
            "message": "Purchase invoice list fetched successfully.",
            "data": serializer.data
        })
