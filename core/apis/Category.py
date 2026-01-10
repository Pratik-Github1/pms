from django.db.models import Q
from apps.models import Category
from rest_framework import status
from django.http import JsonResponse
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.db import transaction, IntegrityError
from rest_framework.pagination import PageNumberPagination

import logging
logger = logging.getLogger(__name__)


class CategoryCRUDView(APIView):
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
            response_data["message"] = "Category name is required."
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        if Category.objects.filter(name=name).exists():
            response_data["message"] = "Category with this name already exists."
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                category = Category.objects.create(
                    name=name.strip(),
                    description=data.get("description")
                )

            response_data["status"] = True
            response_data["message"] = "Category created successfully."
            response_data["data"] = {"id": category.id}
            return JsonResponse(response_data, status=status.HTTP_201_CREATED)

        except IntegrityError as e:
            response_data["message"] = "Integrity error while creating category."
            response_data["error"] = str(e)
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            response_data["message"] = "An error occurred while creating category."
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

        category_id = request.GET.get("id")

        if not category_id:
            response_data["message"] = "Category ID is required."
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            category = Category.objects.get(id=category_id)

            response_data["status"] = True
            response_data["message"] = "Category fetched successfully."
            response_data["data"] = {
                "id": category.id,
                "name": category.name,
                "description": category.description
            }
            return JsonResponse(response_data, status=status.HTTP_200_OK)

        except Category.DoesNotExist:
            response_data["message"] = "Category not found."
            return JsonResponse(response_data, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            response_data["message"] = "An error occurred while fetching category."
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
        category_id = data.get("id")

        if not category_id:
            response_data["message"] = "Category ID is required."
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            category = Category.objects.get(id=category_id)

            allowed_fields = ["name", "description"]
            updated = False

            if "name" in data:
                name = data.get("name")
                if not name:
                    response_data["message"] = "Category name cannot be empty."
                    return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

                if Category.objects.exclude(id=category_id).filter(name=name).exists():
                    response_data["message"] = "Category with this name already exists."
                    return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

            for field in allowed_fields:
                if field in data:
                    setattr(category, field, data.get(field))
                    updated = True

            if not updated:
                response_data["message"] = "No valid fields provided for update."
                return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

            category.save()

            response_data["status"] = True
            response_data["message"] = "Category updated successfully."
            return JsonResponse(response_data, status=status.HTTP_200_OK)

        except Category.DoesNotExist:
            response_data["message"] = "Category not found."
            return JsonResponse(response_data, status=status.HTTP_404_NOT_FOUND)

        except IntegrityError as e:
            response_data["message"] = "Integrity error while updating category."
            response_data["error"] = str(e)
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            response_data["message"] = "An error occurred while updating category."
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

        category_id = request.GET.get("id")

        if not category_id:
            response_data["message"] = "Category ID is required."
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            category = Category.objects.get(id=category_id)
            category.delete()

            response_data["status"] = True
            response_data["message"] = "Category deleted successfully."
            return JsonResponse(response_data, status=status.HTTP_200_OK)

        except Category.DoesNotExist:
            response_data["message"] = "Category not found."
            return JsonResponse(response_data, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            response_data["message"] = "An error occurred while deleting category."
            response_data["error"] = str(e)
            return JsonResponse(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "description",
            "created_at",
        ]

class StandardResultsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class CategoryListView(APIView):
    """
    List Categories with Pagination & Search
    """

    def get(self, request):
        search = request.GET.get("search", "").strip()

        queryset = Category.objects.all().order_by("-id")

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        paginator = StandardResultsPagination()
        paginated_qs = paginator.paginate_queryset(queryset, request)

        serializer = CategoryListSerializer(paginated_qs, many=True)

        return paginator.get_paginated_response({
            "status": True,
            "message": "Category list fetched successfully.",
            "data": serializer.data
        })
