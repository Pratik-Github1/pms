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
        files = request.FILES
        store_name = data.get("store_name")
        logo = files.get("logo")

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
                    gst_number=data.get("gst_number"),
                    drug_license_number=data.get("drug_license_number"),
                    invoice_prefix=data.get("invoice_prefix", "PMS"),
                    invoice_footer_note=data.get("invoice_footer_note"),
                    logo=logo
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
        files = request.FILES

        store_id = data.get("id")
        logo = files.get("logo")  # ✅ Correct

        if not store_id:
            response_data["message"] = "Store ID is required."
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            store = StoreProfile.objects.get(id=store_id)

            allowed_fields = [
                "store_name", "owner_name", "address_line", "city", "state",
                "pincode", "country", "gst_number",
                "drug_license_number", "invoice_prefix", "invoice_footer_note"
            ]

            updated = False

            for field in allowed_fields:
                if field in data:
                    setattr(store, field, data.get(field))
                    updated = True

            if logo:
                store.logo = logo
                updated = True

            if not updated:
                response_data["message"] = "No valid fields provided for update."
                return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

            store.save()

            response_data["status"] = True
            response_data["message"] = "Store profile updated successfully."
            response_data["data"] = {
                "logo": store.logo.url if store.logo else None
            }
            return JsonResponse(response_data, status=status.HTTP_200_OK)

        except StoreProfile.DoesNotExist:
            response_data["message"] = "Store profile not found."
            return JsonResponse(response_data, status=status.HTTP_404_NOT_FOUND)

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
        
class GETStoreProfileInformation(APIView):
    def get(self, request, *args, **kwargs):
        response_date = {"status": False, "message": "", "data": None}
        try:
            store_profile = StoreProfile.objects.get(id=1)
            data = {
                "id": store_profile.id,
                "store_name": store_profile.store_name,
                "owner_name": store_profile.owner_name,
                "gst_number": store_profile.gst_number,
                "drug_license_number": store_profile.drug_license_number,
                "city": store_profile.city,
                "state": store_profile.state,
                "pincode": store_profile.pincode,
                "country": store_profile.country,
                "address_line": store_profile.address_line,
                "invoice_footer_note": store_profile.invoice_footer_note,
                "logo": store_profile.logo.url if store_profile.logo else None,
            }
            if data:
                response_date["status"] = True
                response_date["message"] = "Store profile fetched successfully."
                response_date["data"] = data
                return JsonResponse(response_date, status=status.HTTP_200_OK)
            else:
                response_date["message"] = "Store profile not found."
                return JsonResponse(response_date, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            response_date["message"] = "An error occurred while fetching store profile."
            response_date["error"] = str(e)
            return JsonResponse(response_date, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
