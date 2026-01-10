from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.db import transaction, IntegrityError

from apps.models import Medicine, Category, Manufacturer
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

        name = data.get("name")
        if not name:
            response_data["message"] = "Medicine name is required."
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                medicine = Medicine.objects.create(
                    name=name.strip(),
                    generic_name=data.get("generic_name"),
                    category=Category.objects.filter(id=data.get("category_id")).first(),
                    manufacturer=Manufacturer.objects.filter(id=data.get("manufacturer_id")).first(),
                    hsn_code=data.get("hsn_code"),
                    unit=data.get("unit", "strip"),
                    packing_details=data.get("packing_details"),
                    low_stock_alert=data.get("low_stock_alert", 0),
                    is_active=data.get("is_active", True),
                )

            response_data["status"] = True
            response_data["message"] = "Medicine created successfully."
            response_data["data"] = {"id": medicine.id}
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
            medicine = Medicine.objects.get(id=medicine_id)

            response_data["status"] = True
            response_data["message"] = "Medicine fetched successfully."
            response_data["data"] = {
                "id": medicine.id,
                "name": medicine.name,
                "generic_name": medicine.generic_name,
                "category_id": medicine.category_id,
                "manufacturer_id": medicine.manufacturer_id,
                "hsn_code": medicine.hsn_code,
                "unit": medicine.unit,
                "packing_details": medicine.packing_details,
                "low_stock_alert": medicine.low_stock_alert,
                "is_active": medicine.is_active,
            }
            return JsonResponse(response_data, status=status.HTTP_200_OK)

        except Medicine.DoesNotExist:
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
            medicine = Medicine.objects.get(id=medicine_id)

            allowed_fields = [
                "name", "generic_name", "hsn_code", "unit",
                "packing_details", "low_stock_alert", "is_active"
            ]

            updated = False
            for field in allowed_fields:
                if field in data:
                    setattr(medicine, field, data.get(field))
                    updated = True

            if "category_id" in data:
                medicine.category = Category.objects.filter(id=data.get("category_id")).first()
                updated = True

            if "manufacturer_id" in data:
                medicine.manufacturer = Manufacturer.objects.filter(id=data.get("manufacturer_id")).first()
                updated = True

            if not updated:
                response_data["message"] = "No valid fields provided for update."
                return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

            medicine.save()
            response_data["status"] = True
            response_data["message"] = "Medicine updated successfully."
            return JsonResponse(response_data, status=status.HTTP_200_OK)

        except Medicine.DoesNotExist:
            response_data["message"] = "Medicine not found."
            return JsonResponse(response_data, status=status.HTTP_404_NOT_FOUND)


from apps.models import MedicineBatch, Medicine, RackLocation


class MedicineBatchCRUDView(APIView):
    permission_classes = [AllowAny]

    # -------------------------
    # CREATE
    # -------------------------
    def post(self, request):
        response_data = {"status": False, "message": "", "data": None, "error": None}
        data = request.data

        required = ["medicine_id", "batch_number", "purchase_price", "mrp", "selling_price"]
        if not all(field in data for field in required):
            response_data["message"] = "Missing required fields."
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                batch = MedicineBatch.objects.create(
                    medicine=Medicine.objects.get(id=data["medicine_id"]),
                    batch_number=data["batch_number"],
                    manufacturing_date=data.get("manufacturing_date"),
                    expiry_date=data.get("expiry_date"),
                    rack_location=RackLocation.objects.filter(id=data.get("rack_location_id")).first(),
                    purchase_price=data["purchase_price"],
                    mrp=data["mrp"],
                    selling_price=data["selling_price"],
                    current_stock=data.get("current_stock", 0),
                    is_active=data.get("is_active", True),
                )

            response_data["status"] = True
            response_data["message"] = "Medicine batch created successfully."
            response_data["data"] = {"id": batch.id}
            return JsonResponse(response_data, status=status.HTTP_201_CREATED)

        except IntegrityError as e:
            response_data["message"] = "Batch already exists for this medicine."
            response_data["error"] = str(e)
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

    # -------------------------
    # READ (BY ID ONLY)
    # -------------------------
    def get(self, request):
        response_data = {"status": False, "message": "", "data": None, "error": None}
        batch_id = request.GET.get("id")

        if not batch_id:
            response_data["message"] = "Batch ID is required."
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            batch = MedicineBatch.objects.get(id=batch_id)

            response_data["status"] = True
            response_data["message"] = "Medicine batch fetched successfully."
            response_data["data"] = {
                "id": batch.id,
                "medicine_id": batch.medicine_id,
                "batch_number": batch.batch_number,
                "manufacturing_date": batch.manufacturing_date,
                "expiry_date": batch.expiry_date,
                "rack_location_id": batch.rack_location_id,
                "purchase_price": batch.purchase_price,
                "mrp": batch.mrp,
                "selling_price": batch.selling_price,
                "current_stock": batch.current_stock,
                "is_active": batch.is_active,
            }
            return JsonResponse(response_data, status=status.HTTP_200_OK)

        except MedicineBatch.DoesNotExist:
            response_data["message"] = "Medicine batch not found."
            return JsonResponse(response_data, status=status.HTTP_404_NOT_FOUND)

    # -------------------------
    # UPDATE (PARTIAL)
    # -------------------------
    def patch(self, request):
        response_data = {"status": False, "message": "", "error": None}
        data = request.data
        batch_id = data.get("id")

        if not batch_id:
            response_data["message"] = "Batch ID is required."
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            batch = MedicineBatch.objects.get(id=batch_id)

            allowed_fields = [
                "batch_number", "manufacturing_date", "expiry_date",
                "purchase_price", "mrp", "selling_price",
                "current_stock", "is_active"
            ]

            updated = False
            for field in allowed_fields:
                if field in data:
                    setattr(batch, field, data.get(field))
                    updated = True

            if "rack_location_id" in data:
                batch.rack_location = RackLocation.objects.filter(id=data.get("rack_location_id")).first()
                updated = True

            if not updated:
                response_data["message"] = "No valid fields provided for update."
                return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

            batch.save()
            response_data["status"] = True
            response_data["message"] = "Medicine batch updated successfully."
            return JsonResponse(response_data, status=status.HTTP_200_OK)

        except MedicineBatch.DoesNotExist:
            response_data["message"] = "Medicine batch not found."
            return JsonResponse(response_data, status=status.HTTP_404_NOT_FOUND)

    # -------------------------
    # DELETE
    # -------------------------
    def delete(self, request):
        response_data = {"status": False, "message": "", "error": None}
        batch_id = request.GET.get("id")

        if not batch_id:
            response_data["message"] = "Batch ID is required."
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            MedicineBatch.objects.get(id=batch_id).delete()
            response_data["status"] = True
            response_data["message"] = "Medicine batch deleted successfully."
            return JsonResponse(response_data, status=status.HTTP_200_OK)

        except MedicineBatch.DoesNotExist:
            response_data["message"] = "Medicine batch not found."
            return JsonResponse(response_data, status=status.HTTP_404_NOT_FOUND)
