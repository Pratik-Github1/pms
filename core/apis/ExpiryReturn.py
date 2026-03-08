from decimal import Decimal
from django.http import JsonResponse
from django.db.models import Q, Sum, Subquery, OuterRef
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from django.db import transaction

from apps.models import (
    ExpiryReturn,
    ExpiryReturnItem,
    Supplier,
    MedicineInventory,
)

import logging
logger = logging.getLogger(__name__)


class ExpiryReturnCRUDView(APIView):
    permission_classes = [AllowAny]

    # -------------------------
    # CREATE
    # -------------------------
    def post(self, request):
        data = request.data

        supplier_id = data.get("supplier_id")
        items = data.get("items")

        if not supplier_id:
            return JsonResponse(
                {"status": False, "message": "supplier_id is required"},
                status=400
            )

        if not items or not isinstance(items, list):
            return JsonResponse(
                {"status": False, "message": "At least one item is required"},
                status=400
            )

        try:
            with transaction.atomic():
                # Auto-generate return number
                last = ExpiryReturn.objects.order_by("-id").first()
                next_num = (last.id + 1) if last else 1
                return_number = f"ER-{next_num:04d}"

                expiry_return = ExpiryReturn.objects.create(
                    supplier_id=supplier_id,
                    return_number=return_number,
                    remarks=data.get("remarks", ""),
                    total_amount=0,
                )

                total_amount = Decimal("0.00")

                for idx, item in enumerate(items, start=1):
                    medicine_id = item.get("medicine_id")
                    quantity = item.get("quantity")
                    rate = item.get("rate", 0)

                    if not medicine_id or not quantity:
                        raise ValueError(f"Invalid item at position {idx}")

                    medicine = MedicineInventory.objects.select_for_update().get(id=medicine_id)
                    qty = int(quantity)

                    # Stock outward
                    medicine.current_stock = max(0, medicine.current_stock - qty)
                    medicine.save(update_fields=["current_stock"])

                    line_total = Decimal(str(rate)) * qty

                    ExpiryReturnItem.objects.create(
                        expiry_return_id=expiry_return.id,
                        medicine_id=medicine_id,
                        batch_number=medicine.batch_number,
                        quantity=qty,
                        rate=rate,
                    )

                    total_amount += line_total

                expiry_return.total_amount = total_amount
                expiry_return.save(update_fields=["total_amount"])

            return JsonResponse({
                "status": True,
                "message": "Expiry return created successfully",
                "data": {"id": expiry_return.id, "return_number": return_number}
            }, status=201)

        except MedicineInventory.DoesNotExist:
            return JsonResponse({"status": False, "message": "Invalid medicine ID"}, status=400)
        except Exception as e:
            logger.exception("Expiry Return Creation Failed")
            return JsonResponse({"status": False, "message": str(e)}, status=500)

    # -------------------------
    # GET (BY ID)
    # -------------------------
    def get(self, request):
        return_id = request.GET.get("id")
        if not return_id:
            return JsonResponse({"status": False, "message": "Expiry return ID required"}, status=400)

        try:
            er = ExpiryReturn.objects.get(id=return_id)
            items = ExpiryReturnItem.objects.filter(expiry_return_id=er.id)

            # Get supplier name
            supplier = Supplier.objects.filter(id=er.supplier_id).values("company_name").first()

            items_data = []
            for item in items:
                med = MedicineInventory.objects.filter(id=item.medicine_id).values("name").first()
                items_data.append({
                    "id": item.id,
                    "medicine_id": item.medicine_id,
                    "medicine_name": med["name"] if med else "Unknown",
                    "batch_number": item.batch_number,
                    "quantity": item.quantity,
                    "rate": str(item.rate),
                })

            return JsonResponse({
                "status": True,
                "data": {
                    "expiry_return": {
                        "id": er.id,
                        "return_number": er.return_number,
                        "supplier_id": er.supplier_id,
                        "supplier_name": supplier["company_name"] if supplier else "Unknown",
                        "return_date": er.return_date,
                        "total_amount": str(er.total_amount),
                        "remarks": er.remarks,
                        "is_returned": er.is_returned,
                    },
                    "items": items_data,
                }
            })

        except ExpiryReturn.DoesNotExist:
            return JsonResponse({"status": False, "message": "Expiry return not found"}, status=404)


class ExpiryReturnListSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(read_only=True)
    total_items = serializers.IntegerField(read_only=True)

    class Meta:
        model = ExpiryReturn
        fields = [
            "id", "return_number", "supplier_id", "supplier_name",
            "return_date", "total_amount", "remarks", "is_returned",
            "total_items", "created_at",
        ]


class StandardResultsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class ExpiryReturnListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        search = request.GET.get("search", "").strip()

        supplier_name_sq = Supplier.objects.filter(
            id=OuterRef("supplier_id")
        ).values("company_name")[:1]

        queryset = ExpiryReturn.objects.annotate(
            supplier_name=Subquery(supplier_name_sq),
            total_items=Sum("id")  # placeholder — we count items below
        ).order_by("-id")

        # Actually annotate total_items properly
        from django.db.models import Count
        queryset = ExpiryReturn.objects.annotate(
            supplier_name=Subquery(supplier_name_sq),
        ).order_by("-id")

        if search:
            queryset = queryset.filter(
                Q(return_number__icontains=search) |
                Q(remarks__icontains=search) |
                Q(supplier_name__icontains=search)
            )

        paginator = StandardResultsPagination()
        paginated_qs = paginator.paginate_queryset(queryset, request)

        # Build response data manually to include total_items
        data = []
        for er in paginated_qs:
            items_count = ExpiryReturnItem.objects.filter(expiry_return_id=er.id).count()
            data.append({
                "id": er.id,
                "return_number": er.return_number,
                "supplier_id": er.supplier_id,
                "supplier_name": er.supplier_name or "-",
                "return_date": er.return_date,
                "total_amount": str(er.total_amount),
                "remarks": er.remarks,
                "is_returned": er.is_returned,
                "total_items": items_count,
                "created_at": er.created_at,
            })

        return paginator.get_paginated_response({
            "status": True,
            "message": "Expiry return list fetched.",
            "data": data
        })
