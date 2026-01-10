from decimal import Decimal
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.db import transaction
from django.utils import timezone
from django.db.models import Sum

from apps.models import (
    ExpiryReturn,
    ExpiryReturnItem,
    Supplier,
    Users,
    MedicineBatch
)

class ExpiryReturnCRUDView(APIView):
    permission_classes = [AllowAny]

    # -------------------------
    # CREATE
    # -------------------------
    def post(self, request):
        data = request.data

        if not data.get("return_number") or not data.get("supplier_id"):
            return JsonResponse(
                {"status": False, "message": "return_number and supplier_id are required"},
                status=400
            )

        try:
            supplier = Supplier.objects.get(id=data["supplier_id"])

            with transaction.atomic():
                expiry_return = ExpiryReturn.objects.create(
                    return_number=data["return_number"].strip(),
                    supplier=supplier,
                    return_date=data.get("return_date", timezone.now().date()),
                    remarks=data.get("remarks"),
                    created_by=Users.objects.filter(
                        id=data.get("created_by")
                    ).first(),
                )

            return JsonResponse(
                {
                    "status": True,
                    "message": "Expiry return created successfully",
                    "data": {"id": expiry_return.id},
                },
                status=201
            )

        except Supplier.DoesNotExist:
            return JsonResponse(
                {"status": False, "message": "Supplier not found"},
                status=404
            )

        except Exception as e:
            return JsonResponse(
                {"status": False, "message": str(e)},
                status=500
            )

    # -------------------------
    # GET (BY ID)
    # -------------------------
    def get(self, request):
        return_id = request.GET.get("id")
        if not return_id:
            return JsonResponse(
                {"status": False, "message": "Expiry return ID required"},
                status=400
            )

        try:
            expiry_return = ExpiryReturn.objects.get(id=return_id)

            return JsonResponse(
                {
                    "status": True,
                    "message": "Expiry return fetched successfully",
                    "data": {
                        "id": expiry_return.id,
                        "return_number": expiry_return.return_number,
                        "supplier_id": expiry_return.supplier_id,
                        "return_date": expiry_return.return_date,
                        "total_amount": expiry_return.total_amount,
                        "remarks": expiry_return.remarks,
                    },
                },
                status=200
            )

        except ExpiryReturn.DoesNotExist:
            return JsonResponse(
                {"status": False, "message": "Expiry return not found"},
                status=404
            )

    # -------------------------
    # UPDATE (PARTIAL – HEADER ONLY)
    # -------------------------
    def patch(self, request):
        data = request.data
        return_id = data.get("id")

        if not return_id:
            return JsonResponse(
                {"status": False, "message": "Expiry return ID required"},
                status=400
            )

        try:
            expiry_return = ExpiryReturn.objects.get(id=return_id)

            updated = False
            for field in ["return_date", "remarks"]:
                if field in data:
                    setattr(expiry_return, field, data[field])
                    updated = True

            if "supplier_id" in data:
                expiry_return.supplier = Supplier.objects.get(
                    id=data["supplier_id"]
                )
                updated = True

            if not updated:
                return JsonResponse(
                    {"status": False, "message": "No valid fields to update"},
                    status=400
                )

            expiry_return.save()
            return JsonResponse(
                {"status": True, "message": "Expiry return updated successfully"},
                status=200
            )

        except ExpiryReturn.DoesNotExist:
            return JsonResponse(
                {"status": False, "message": "Expiry return not found"},
                status=404
            )

    # -------------------------
    # DELETE
    # -------------------------
    def delete(self, request):
        return_id = request.GET.get("id")
        if not return_id:
            return JsonResponse(
                {"status": False, "message": "Expiry return ID required"},
                status=400
            )

        try:
            ExpiryReturn.objects.get(id=return_id).delete()
            return JsonResponse(
                {"status": True, "message": "Expiry return deleted successfully"},
                status=200
            )

        except ExpiryReturn.DoesNotExist:
            return JsonResponse(
                {"status": False, "message": "Expiry return not found"},
                status=404
            )


class ExpiryReturnItemCRUDView(APIView):
    permission_classes = [AllowAny]

    # -------------------------
    # CREATE (STOCK OUTWARD)
    # -------------------------
    def post(self, request):
        data = request.data

        required = [
            "expiry_return_id",
            "medicine_batch_id",
            "quantity",
            "rate",
        ]

        if not all(data.get(f) is not None for f in required):
            return JsonResponse(
                {"status": False, "message": "Missing required fields"},
                status=400
            )

        try:
            expiry_return = ExpiryReturn.objects.get(
                id=data["expiry_return_id"]
            )
            batch = MedicineBatch.objects.get(
                id=data["medicine_batch_id"]
            )

            quantity = int(data["quantity"])

            if batch.current_stock < quantity:
                return JsonResponse(
                    {"status": False, "message": "Insufficient stock for expiry return"},
                    status=400
                )

            rate = Decimal(data["rate"])
            line_total = rate * quantity

            with transaction.atomic():
                item = ExpiryReturnItem.objects.create(
                    expiry_return=expiry_return,
                    medicine_batch=batch,
                    quantity=quantity,
                    rate=rate,
                    line_total=line_total,
                )

                # 🔻 STOCK OUTWARD
                batch.current_stock -= quantity
                batch.save(update_fields=["current_stock"])

                # 🔁 Recalculate return total
                total = ExpiryReturnItem.objects.filter(
                    expiry_return=expiry_return
                ).aggregate(total=Sum("line_total"))["total"] or Decimal("0.00")

                expiry_return.total_amount = total
                expiry_return.save(update_fields=["total_amount"])

            return JsonResponse(
                {
                    "status": True,
                    "message": "Expiry return item added successfully",
                    "data": {"id": item.id},
                },
                status=201
            )

        except ExpiryReturn.DoesNotExist:
            return JsonResponse(
                {"status": False, "message": "Expiry return not found"},
                status=404
            )

        except MedicineBatch.DoesNotExist:
            return JsonResponse(
                {"status": False, "message": "Medicine batch not found"},
                status=404
            )

    # -------------------------
    # GET (BY ID)
    # -------------------------
    def get(self, request):
        item_id = request.GET.get("id")
        if not item_id:
            return JsonResponse(
                {"status": False, "message": "Item ID required"},
                status=400
            )

        try:
            item = ExpiryReturnItem.objects.get(id=item_id)

            return JsonResponse(
                {
                    "status": True,
                    "message": "Expiry return item fetched successfully",
                    "data": {
                        "id": item.id,
                        "expiry_return_id": item.expiry_return_id,
                        "medicine_batch_id": item.medicine_batch_id,
                        "quantity": item.quantity,
                        "rate": item.rate,
                        "line_total": item.line_total,
                    },
                },
                status=200
            )

        except ExpiryReturnItem.DoesNotExist:
            return JsonResponse(
                {"status": False, "message": "Expiry return item not found"},
                status=404
            )

    # -------------------------
    # UPDATE (STOCK SAFE)
    # -------------------------
    def patch(self, request):
        data = request.data
        item_id = data.get("id")

        if not item_id:
            return JsonResponse(
                {"status": False, "message": "Item ID required"},
                status=400
            )

        try:
            item = ExpiryReturnItem.objects.select_related(
                "medicine_batch",
                "expiry_return"
            ).get(id=item_id)

            batch = item.medicine_batch
            expiry_return = item.expiry_return

            old_qty = item.quantity
            new_qty = int(data.get("quantity", old_qty))
            qty_diff = new_qty - old_qty

            # qty_diff > 0 → more stock required
            if qty_diff > 0 and batch.current_stock < qty_diff:
                return JsonResponse(
                    {"status": False, "message": "Insufficient stock"},
                    status=400
                )

            with transaction.atomic():
                # adjust stock
                batch.current_stock -= qty_diff
                batch.save(update_fields=["current_stock"])

                if "rate" in data:
                    item.rate = Decimal(data["rate"])

                item.quantity = new_qty
                item.line_total = item.rate * item.quantity
                item.save()

                total = ExpiryReturnItem.objects.filter(
                    expiry_return=expiry_return
                ).aggregate(total=Sum("line_total"))["total"] or Decimal("0.00")

                expiry_return.total_amount = total
                expiry_return.save(update_fields=["total_amount"])

            return JsonResponse(
                {"status": True, "message": "Expiry return item updated successfully"},
                status=200
            )

        except ExpiryReturnItem.DoesNotExist:
            return JsonResponse(
                {"status": False, "message": "Item not found"},
                status=404
            )

    # -------------------------
    # DELETE (ROLLBACK STOCK)
    # -------------------------
    def delete(self, request):
        item_id = request.GET.get("id")
        if not item_id:
            return JsonResponse(
                {"status": False, "message": "Item ID required"},
                status=400
            )

        try:
            item = ExpiryReturnItem.objects.select_related(
                "medicine_batch",
                "expiry_return"
            ).get(id=item_id)

            with transaction.atomic():
                batch = item.medicine_batch
                batch.current_stock += item.quantity
                batch.save(update_fields=["current_stock"])

                expiry_return = item.expiry_return
                item.delete()

                total = ExpiryReturnItem.objects.filter(
                    expiry_return=expiry_return
                ).aggregate(total=Sum("line_total"))["total"] or Decimal("0.00")

                expiry_return.total_amount = total
                expiry_return.save(update_fields=["total_amount"])

            return JsonResponse(
                {"status": True, "message": "Expiry return item deleted and stock reverted"},
                status=200
            )

        except ExpiryReturnItem.DoesNotExist:
            return JsonResponse(
                {"status": False, "message": "Item not found"},
                status=404
            )
