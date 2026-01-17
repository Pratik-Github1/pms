from django.db.models import Q
from rest_framework import status
from django.http import JsonResponse
from rest_framework import serializers
from rest_framework.views import APIView
from apps.models import MedicineInventory
from rest_framework.permissions import AllowAny
from django.db import transaction, IntegrityError
from rest_framework.pagination import PageNumberPagination

import logging
logger = logging.getLogger(__name__)

class MedicineCRUDView(APIView):
    permission_classes = [AllowAny]

    # -------------------------
    # CREATE
    # -------------------------
    def post(self, request):
        response_data = {"status": False, "message": "", "data": None, "error": None}
        data = request.data

        required_fields = [
            "name", "batch_number", "manufacturing_date",
            "expiry_date", "packing_details", "rack_location",
            "purchase_price", "mrp"
        ]

        missing_fields = [
            field for field in required_fields
            if not data.get(field)
        ]

        if missing_fields:
            response_data["message"] = (
                "Missing required fields: " +
                ", ".join(field.replace("_", " ").upper() for field in missing_fields)
            )
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                MedicineInventory.objects.create(
                    name=str(data.get("name")).strip(),
                    medicine_uses=data.get("medicine_uses"),
                    hsn_code=data.get("hsn_code"),
                    unit=data.get("unit", "strip"),
                    packing_details=data.get("packing_details"),
                    low_stock_alert=data.get("low_stock_alert", 0),
                    batch_number=data.get("batch_number"),
                    manufacturing_date=data.get("manufacturing_date"),
                    expiry_date=data.get("expiry_date"),
                    rack_location=data.get("rack_location"),
                    purchase_price=data.get("purchase_price"),
                    mrp=data.get("mrp"),
                    current_stock=data.get("current_stock", 0),
                    is_active=True,
                    is_expired=False,
                )

            response_data["status"] = True
            response_data["message"] = "Medicine created successfully."
            return JsonResponse(response_data, status=status.HTTP_201_CREATED)

        except IntegrityError as e:
            response_data["message"] = "Integrity error while creating medicine."
            response_data["error"] = str(e)
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            response_data["message"] = "An error occurred while creating medicine."
            response_data["error"] = str(e)
            return JsonResponse(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # -------------------------
    # READ (BY ID ONLY)
    # -------------------------
    def get(self, request):
        response_data = {"status": False, "message": "", "data": None, "error": None}
        medicine_id = request.GET.get("id")

        if not medicine_id:
            response_data["message"] = "Medicine ID is required."
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            medicine = MedicineInventory.objects.get(id=medicine_id)

            response_data["status"] = True
            response_data["message"] = "Medicine fetched successfully."
            response_data["data"] = {
                "id": medicine.id,
                "name": medicine.name,
                "medicine_uses": medicine.medicine_uses,
                "hsn_code": medicine.hsn_code,
                "unit": medicine.unit,
                "packing_details": medicine.packing_details,
                "low_stock_alert": medicine.low_stock_alert,
                "batch_number": medicine.batch_number,
                "manufacturing_date": medicine.manufacturing_date,
                "expiry_date": medicine.expiry_date,
                "rack_location": medicine.rack_location,
                "purchase_price": medicine.purchase_price,
                "mrp": medicine.mrp,
                "current_stock": medicine.current_stock,
                "is_active": medicine.is_active,
                "is_expired": medicine.is_expired,
            }
            return JsonResponse(response_data, status=status.HTTP_200_OK)

        except MedicineInventory.DoesNotExist:
            response_data["message"] = "Medicine not found."
            return JsonResponse(response_data, status=status.HTTP_404_NOT_FOUND)

    # -------------------------
    # UPDATE (PARTIAL)
    # -------------------------
    def patch(self, request):
        response_data = {"status": False, "message": "", "error": None}
        data = request.data
        medicine_id = data.get("id")

        if not medicine_id:
            response_data["message"] = "Medicine ID is required."
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            medicine = MedicineInventory.objects.get(id=medicine_id)

            allowed_fields = [
                "name",
                "medicine_uses",
                "hsn_code",
                "unit",
                "packing_details",
                "low_stock_alert",
                "rack_location",
                "purchase_price",
                "mrp",
                "current_stock",
                "is_active",
                "is_expired",
            ]

            updated = False
            for field in allowed_fields:
                if field in data:
                    setattr(medicine, field, data.get(field))
                    updated = True

            if not updated:
                response_data["message"] = "No valid fields provided for update."
                return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

            medicine.save()
            response_data["status"] = True
            response_data["message"] = "Medicine updated successfully."
            return JsonResponse(response_data, status=status.HTTP_200_OK)

        except MedicineInventory.DoesNotExist:
            response_data["message"] = "Medicine not found."
            return JsonResponse(response_data, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            response_data["message"] = "An error occurred while updating medicine."
            response_data["error"] = str(e)
            return JsonResponse(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class MedicineInventoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicineInventory
        fields = [
            "id",
            "name",
            "medicine_uses",
            "low_stock_alert",
            "batch_number",
            "manufacturing_date",
            "expiry_date",
            "rack_location",
            "mrp",
            "current_stock",
            "is_active",
            "is_expired",
            "created_at",
        ]


class StandardResultsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class MedicineInventoryListView(APIView):
    """
    List Medicine Inventory with Pagination & Search
    """

    def get(self, request):
        search = request.GET.get("search", "").strip()

        queryset = MedicineInventory.objects.all().order_by("-id")

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(medicine_uses__icontains=search) |
                Q(rack_location__icontains=search) |
                Q(batch_number__icontains=search)
            )

        paginator = StandardResultsPagination()
        paginated_qs = paginator.paginate_queryset(queryset, request)

        serializer = MedicineInventoryListSerializer(paginated_qs, many=True)

        return paginator.get_paginated_response({
            "status": True,
            "message": "Medicine inventory list fetched successfully.",
            "data": serializer.data
        })

class GetMedicineInventoryListSmall(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        suppliers = MedicineInventory.objects.values(
            "id",
            "name"
        ).order_by("-id")

        return JsonResponse({
            "status": True,
            "message": "Supplier list fetched successfully.",
            "data": list(suppliers)
        })