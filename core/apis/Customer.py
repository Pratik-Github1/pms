from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.db import transaction, IntegrityError

from apps.models import Customer
import logging

logger = logging.getLogger(__name__)


class CustomerCRUDView(APIView):
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
            response_data["message"] = "Customer name is required."
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                customer = Customer.objects.create(
                    name=name.strip(),
                    phone=data.get("phone"),
                    email=data.get("email"),
                    address=data.get("address"),
                    date_of_birth=data.get("date_of_birth"),
                    notes=data.get("notes"),
                    is_active=data.get("is_active", True),
                )

            response_data["status"] = True
            response_data["message"] = "Customer created successfully."
            response_data["data"] = {"id": customer.id}
            return JsonResponse(response_data, status=status.HTTP_201_CREATED)

        except IntegrityError as e:
            response_data["message"] = "Integrity error while creating customer."
            response_data["error"] = str(e)
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            response_data["message"] = "An error occurred while creating customer."
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

        customer_id = request.GET.get("id")

        if not customer_id:
            response_data["message"] = "Customer ID is required."
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            customer = Customer.objects.get(id=customer_id)

            response_data["status"] = True
            response_data["message"] = "Customer fetched successfully."
            response_data["data"] = {
                "id": customer.id,
                "name": customer.name,
                "phone": customer.phone,
                "email": customer.email,
                "address": customer.address,
                "date_of_birth": customer.date_of_birth,
                "notes": customer.notes,
                "is_active": customer.is_active,
            }
            return JsonResponse(response_data, status=status.HTTP_200_OK)

        except Customer.DoesNotExist:
            response_data["message"] = "Customer not found."
            return JsonResponse(response_data, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            response_data["message"] = "An error occurred while fetching customer."
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
        customer_id = data.get("id")

        if not customer_id:
            response_data["message"] = "Customer ID is required."
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            customer = Customer.objects.get(id=customer_id)

            allowed_fields = [
                "name", "phone", "email", "address",
                "date_of_birth", "notes", "is_active"
            ]

            if "name" in data:
                name = data.get("name")
                if not name:
                    response_data["message"] = "Customer name cannot be empty."
                    return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

            updated = False
            for field in allowed_fields:
                if field in data:
                    setattr(customer, field, data.get(field))
                    updated = True

            if not updated:
                response_data["message"] = "No valid fields provided for update."
                return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

            customer.save()

            response_data["status"] = True
            response_data["message"] = "Customer updated successfully."
            return JsonResponse(response_data, status=status.HTTP_200_OK)

        except Customer.DoesNotExist:
            response_data["message"] = "Customer not found."
            return JsonResponse(response_data, status=status.HTTP_404_NOT_FOUND)

        except IntegrityError as e:
            response_data["message"] = "Integrity error while updating customer."
            response_data["error"] = str(e)
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            response_data["message"] = "An error occurred while updating customer."
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

        customer_id = request.GET.get("id")

        if not customer_id:
            response_data["message"] = "Customer ID is required."
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            customer = Customer.objects.get(id=customer_id)
            customer.delete()

            response_data["status"] = True
            response_data["message"] = "Customer deleted successfully."
            return JsonResponse(response_data, status=status.HTTP_200_OK)

        except Customer.DoesNotExist:
            response_data["message"] = "Customer not found."
            return JsonResponse(response_data, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            response_data["message"] = "An error occurred while deleting customer."
            response_data["error"] = str(e)
            return JsonResponse(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
