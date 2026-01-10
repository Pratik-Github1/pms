from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.db import transaction, IntegrityError

from apps.models import StoreProfile
import logging

logger = logging.getLogger(__name__)


class StoreProfileCRUDView(APIView):
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
        store_name = data.get("store_name")

        if not store_name:
            response_data["message"] = "Store name is required."
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        if StoreProfile.objects.filter(store_name=store_name).exists():
            response_data["message"] = "Store with this name already exists."
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                store = StoreProfile.objects.create(
                    store_name=store_name,
                    owner_name=data.get("owner_name"),
                    address_line=data.get("address_line"),
                    city=data.get("city"),
                    state=data.get("state"),
                    pincode=data.get("pincode"),
                    country=data.get("country", "India"),
                    phone=data.get("phone"),
                    email=data.get("email"),
                    gst_number=data.get("gst_number"),
                    drug_license_number=data.get("drug_license_number"),
                    invoice_prefix=data.get("invoice_prefix", "PMS"),
                    invoice_footer_note=data.get("invoice_footer_note"),
                    logo=data.get("logo"),
                )

            response_data["status"] = True
            response_data["message"] = "Store profile created successfully."
            response_data["data"] = {"id": store.id}
            return JsonResponse(response_data, status=status.HTTP_201_CREATED)

        except IntegrityError as e:
            response_data["message"] = "Integrity error while creating store profile."
            response_data["error"] = str(e)
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            response_data["message"] = "An error occurred while creating store profile."
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

        store_id = request.GET.get("id")

        if not store_id:
            response_data["message"] = "Store ID is required."
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            store = StoreProfile.objects.get(id=store_id)

            response_data["status"] = True
            response_data["message"] = "Store profile fetched successfully."
            response_data["data"] = {
                "id": store.id,
                "store_name": store.store_name,
                "owner_name": store.owner_name,
                "address_line": store.address_line,
                "city": store.city,
                "state": store.state,
                "pincode": store.pincode,
                "country": store.country,
                "phone": store.phone,
                "email": store.email,
                "gst_number": store.gst_number,
                "drug_license_number": store.drug_license_number,
                "invoice_prefix": store.invoice_prefix,
                "invoice_footer_note": store.invoice_footer_note,
                "logo": store.logo.url if store.logo else None,
            }

            return JsonResponse(response_data, status=status.HTTP_200_OK)

        except StoreProfile.DoesNotExist:
            response_data["message"] = "Store profile not found."
            return JsonResponse(response_data, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            response_data["message"] = "An error occurred while fetching store profile."
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
        store_id = data.get("id")

        if not store_id:
            response_data["message"] = "Store ID is required."
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            store = StoreProfile.objects.get(id=store_id)

            allowed_fields = [
                "store_name", "owner_name", "address_line", "city", "state",
                "pincode", "country", "phone", "email", "gst_number",
                "drug_license_number", "invoice_prefix", "invoice_footer_note", "logo"
            ]

            updated = False
            for field in allowed_fields:
                if field in data:
                    setattr(store, field, data.get(field))
                    updated = True

            if not updated:
                response_data["message"] = "No valid fields provided for update."
                return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

            store.save()

            response_data["status"] = True
            response_data["message"] = "Store profile updated successfully."
            return JsonResponse(response_data, status=status.HTTP_200_OK)

        except StoreProfile.DoesNotExist:
            response_data["message"] = "Store profile not found."
            return JsonResponse(response_data, status=status.HTTP_404_NOT_FOUND)

        except IntegrityError as e:
            response_data["message"] = "Integrity error while updating store profile."
            response_data["error"] = str(e)
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            response_data["message"] = "An error occurred while updating store profile."
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

        store_id = request.GET.get("id")

        if not store_id:
            response_data["message"] = "Store ID is required."
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            store = StoreProfile.objects.get(id=store_id)
            store.delete()

            response_data["status"] = True
            response_data["message"] = "Store profile deleted successfully."
            return JsonResponse(response_data, status=status.HTTP_200_OK)

        except StoreProfile.DoesNotExist:
            response_data["message"] = "Store profile not found."
            return JsonResponse(response_data, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            response_data["message"] = "An error occurred while deleting store profile."
            response_data["error"] = str(e)
            return JsonResponse(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
