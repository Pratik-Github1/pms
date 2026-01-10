from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.db import transaction, IntegrityError

from apps.models import Manufacturer
import logging

logger = logging.getLogger(__name__)


class ManufacturerCRUDView(APIView):
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
            response_data["message"] = "Manufacturer name is required."
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        if Manufacturer.objects.filter(name=name).exists():
            response_data["message"] = "Manufacturer with this name already exists."
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                manufacturer = Manufacturer.objects.create(
                    name=name.strip(),
                    contact_person=data.get("contact_person"),
                    phone=data.get("phone"),
                    email=data.get("email"),
                    address=data.get("address"),
                )

            response_data["status"] = True
            response_data["message"] = "Manufacturer created successfully."
            response_data["data"] = {"id": manufacturer.id}
            return JsonResponse(response_data, status=status.HTTP_201_CREATED)

        except IntegrityError as e:
            response_data["message"] = "Integrity error while creating manufacturer."
            response_data["error"] = str(e)
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            response_data["message"] = "An error occurred while creating manufacturer."
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

        manufacturer_id = request.GET.get("id")

        if not manufacturer_id:
            response_data["message"] = "Manufacturer ID is required."
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            manufacturer = Manufacturer.objects.get(id=manufacturer_id)

            response_data["status"] = True
            response_data["message"] = "Manufacturer fetched successfully."
            response_data["data"] = {
                "id": manufacturer.id,
                "name": manufacturer.name,
                "contact_person": manufacturer.contact_person,
                "phone": manufacturer.phone,
                "email": manufacturer.email,
                "address": manufacturer.address,
            }
            return JsonResponse(response_data, status=status.HTTP_200_OK)

        except Manufacturer.DoesNotExist:
            response_data["message"] = "Manufacturer not found."
            return JsonResponse(response_data, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            response_data["message"] = "An error occurred while fetching manufacturer."
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
        manufacturer_id = data.get("id")

        if not manufacturer_id:
            response_data["message"] = "Manufacturer ID is required."
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            manufacturer = Manufacturer.objects.get(id=manufacturer_id)

            allowed_fields = [
                "name", "contact_person", "phone", "email", "address"
            ]

            if "name" in data:
                name = data.get("name")
                if not name:
                    response_data["message"] = "Manufacturer name cannot be empty."
                    return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

                if Manufacturer.objects.exclude(id=manufacturer_id).filter(name=name).exists():
                    response_data["message"] = "Manufacturer with this name already exists."
                    return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

            updated = False
            for field in allowed_fields:
                if field in data:
                    setattr(manufacturer, field, data.get(field))
                    updated = True

            if not updated:
                response_data["message"] = "No valid fields provided for update."
                return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

            manufacturer.save()

            response_data["status"] = True
            response_data["message"] = "Manufacturer updated successfully."
            return JsonResponse(response_data, status=status.HTTP_200_OK)

        except Manufacturer.DoesNotExist:
            response_data["message"] = "Manufacturer not found."
            return JsonResponse(response_data, status=status.HTTP_404_NOT_FOUND)

        except IntegrityError as e:
            response_data["message"] = "Integrity error while updating manufacturer."
            response_data["error"] = str(e)
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            response_data["message"] = "An error occurred while updating manufacturer."
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

        manufacturer_id = request.GET.get("id")

        if not manufacturer_id:
            response_data["message"] = "Manufacturer ID is required."
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            manufacturer = Manufacturer.objects.get(id=manufacturer_id)
            manufacturer.delete()

            response_data["status"] = True
            response_data["message"] = "Manufacturer deleted successfully."
            return JsonResponse(response_data, status=status.HTTP_200_OK)

        except Manufacturer.DoesNotExist:
            response_data["message"] = "Manufacturer not found."
            return JsonResponse(response_data, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            response_data["message"] = "An error occurred while deleting manufacturer."
            response_data["error"] = str(e)
            return JsonResponse(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
