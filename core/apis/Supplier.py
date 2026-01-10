from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.db import transaction, IntegrityError

from apps.models import Supplier
import logging

logger = logging.getLogger(__name__)


class SupplierCRUDView(APIView):
    permission_classes = [AllowAny]

    # -------------------------
    # CREATE
    # -------------------------
    def post(self, request):
        response_data = {
            "status": False,
            "message": "",
            "data": None,
            "error": None
        }

        data = request.data
        name = data.get("name")

        if not name:
            response_data["message"] = "Supplier name is required."
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                supplier = Supplier.objects.create(
                    name=name.strip(),
                    company_name=data.get("company_name"),
                    phone=data.get("phone"),
                    email=data.get("email"),
                    address=data.get("address"),
                    gst_number=data.get("gst_number"),
                    is_active=data.get("is_active", True),
                )

            response_data["status"] = True
            response_data["message"] = "Supplier created successfully."
            response_data["data"] = {"id": supplier.id}
            return JsonResponse(response_data, status=status.HTTP_201_CREATED)

        except IntegrityError as e:
            response_data["message"] = "Integrity error while creating supplier."
            response_data["error"] = str(e)
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            response_data["message"] = "An error occurred while creating supplier."
            response_data["error"] = str(e)
            return JsonResponse(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # -------------------------
    # READ (BY ID ONLY)
    # -------------------------
    def get(self, request):
        response_data = {
            "status": False,
            "message": "",
            "data": None,
            "error": None
        }

        supplier_id = request.GET.get("id")

        if not supplier_id:
            response_data["message"] = "Supplier ID is required."
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            supplier = Supplier.objects.get(id=supplier_id)

            response_data["status"] = True
            response_data["message"] = "Supplier fetched successfully."
            response_data["data"] = {
                "id": supplier.id,
                "name": supplier.name,
                "company_name": supplier.company_name,
                "phone": supplier.phone,
                "email": supplier.email,
                "address": supplier.address,
                "gst_number": supplier.gst_number,
                "is_active": supplier.is_active,
            }
            return JsonResponse(response_data, status=status.HTTP_200_OK)

        except Supplier.DoesNotExist:
            response_data["message"] = "Supplier not found."
            return JsonResponse(response_data, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            response_data["message"] = "An error occurred while fetching supplier."
            response_data["error"] = str(e)
            return JsonResponse(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # -------------------------
    # UPDATE (PARTIAL)
    # -------------------------
    def patch(self, request):
        response_data = {
            "status": False,
            "message": "",
            "data": None,
            "error": None
        }

        data = request.data
        supplier_id = data.get("id")

        if not supplier_id:
            response_data["message"] = "Supplier ID is required."
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            supplier = Supplier.objects.get(id=supplier_id)

            allowed_fields = [
                "name", "company_name", "phone", "email",
                "address", "gst_number", "is_active"
            ]

            if "name" in data:
                name = data.get("name")
                if not name:
                    response_data["message"] = "Supplier name cannot be empty."
                    return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

            updated = False
            for field in allowed_fields:
                if field in data:
                    setattr(supplier, field, data.get(field))
                    updated = True

            if not updated:
                response_data["message"] = "No valid fields provided for update."
                return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

            supplier.save()

            response_data["status"] = True
            response_data["message"] = "Supplier updated successfully."
            return JsonResponse(response_data, status=status.HTTP_200_OK)

        except Supplier.DoesNotExist:
            response_data["message"] = "Supplier not found."
            return JsonResponse(response_data, status=status.HTTP_404_NOT_FOUND)

        except IntegrityError as e:
            response_data["message"] = "Integrity error while updating supplier."
            response_data["error"] = str(e)
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            response_data["message"] = "An error occurred while updating supplier."
            response_data["error"] = str(e)
            return JsonResponse(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # -------------------------
    # DELETE
    # -------------------------
    def delete(self, request):
        response_data = {
            "status": False,
            "message": "",
            "error": None
        }

        supplier_id = request.GET.get("id")

        if not supplier_id:
            response_data["message"] = "Supplier ID is required."
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            supplier = Supplier.objects.get(id=supplier_id)
            supplier.delete()

            response_data["status"] = True
            response_data["message"] = "Supplier deleted successfully."
            return JsonResponse(response_data, status=status.HTTP_200_OK)

        except Supplier.DoesNotExist:
            response_data["message"] = "Supplier not found."
            return JsonResponse(response_data, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            response_data["message"] = "An error occurred while deleting supplier."
            response_data["error"] = str(e)
            return JsonResponse(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
