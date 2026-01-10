from django.db import models
from django.utils import timezone


# ==========================
#  Abstract / Base Models
# ==========================

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# ==========================
#  User & Store Profile
# ==========================

class Users(models.Model):
    """
    Custom user table (no relation to Django's auth.User).
    For now, only one store owner will exist, but structure allows future roles.
    """
    ROLE_CHOICES = [
        ("OWNER", "Owner"),
        ("CASHIER", "Cashier"),
        ("STOCK_MANAGER", "Stock Manager"),
        ("VIEWER", "Viewer"),
    ]

    id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=64, unique=True, db_index=True)
    password = models.CharField(max_length=128)
    full_name = models.CharField(max_length=128)
    mobile_number = models.CharField(max_length=15, blank=True, null=True, db_index=True)
    email = models.EmailField(blank=True, null=True, db_index=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True, db_index=True)
    last_login = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "users"
        indexes = [
            models.Index(fields=["username"]),
            models.Index(fields=["mobile_number"]),
            models.Index(fields=["email"]),
            models.Index(fields=["role"]),
        ]

    def __str__(self):
        return self.username

class BlacklistedToken(models.Model):
    token = models.TextField(db_index=True)
    blacklisted_at = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return self.token

    class Meta:
        managed = False
        db_table = 'blacklisted_token'
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['blacklisted_at']),
        ]

class StoreProfile(TimeStampedModel):
    """
    Single row expected. Stores business info printed on invoice header.
    """
    id = models.BigAutoField(primary_key=True)
    store_name = models.CharField(max_length=255, unique=True, db_index=True)
    owner_name = models.CharField(max_length=255, blank=True, null=True)
    gst_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Printed on invoice only. No GST calculations."
    )
    drug_license_number = models.CharField(max_length=64, blank=True, null=True)
    city = models.CharField(max_length=128, blank=True, null=True)
    state = models.CharField(max_length=128, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    country = models.CharField(max_length=64, default="India")
    address_line = models.CharField(max_length=255, blank=True, null=True)
    invoice_prefix = models.CharField(
        max_length=20,
        default="PMS",
        help_text="Used for invoice numbering, e.g., PMS-00001"
    )
    invoice_footer_note = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to="store_logo/", blank=True, null=True)

    class Meta:
        db_table = "store_profile"

# ==========================
#  Master Data: Category, Manufacturer, Rack
# ==========================

class Category(TimeStampedModel):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=128, unique=True, db_index=True)
    description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "categories"

    def __str__(self):
        return self.name


class Manufacturer(TimeStampedModel):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True, db_index=True)
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "manufacturers"

    def __str__(self):
        return self.name


class RackLocation(TimeStampedModel):
    """
    Represents physical placement – rack, shelf, row etc.
    """
    id = models.BigAutoField(primary_key=True)
    code = models.CharField(max_length=64, unique=True, db_index=True)
    description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = "rack_locations"

    def __str__(self):
        return self.code


# ==========================
#  Medicine & Batch
# ==========================

class Medicine(TimeStampedModel):
    """
    Master product table, batch independent.
    """
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, db_index=True)
    generic_name = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="medicines",
        db_index=True,
    )
    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="medicines",
        db_index=True,
    )
    hsn_code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="For future GST support; not used in current calculations."
    )
    unit = models.CharField(
        max_length=32,
        default="strip",
        help_text="e.g., strip, bottle, tube, vial"
    )
    packing_details = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        help_text="e.g., 10 tablets per strip"
    )
    low_stock_alert = models.IntegerField(
        default=0,
        help_text="If total stock falls below this, show low stock alert."
    )
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "medicines"
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["generic_name"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.name


class MedicineBatch(TimeStampedModel):
    """
    Batch-level stock and pricing. Stock will be maintained here.
    """
    id = models.BigAutoField(primary_key=True)
    medicine = models.ForeignKey(
        Medicine,
        on_delete=models.CASCADE,
        related_name="batches",
        db_index=True,
    )
    batch_number = models.CharField(max_length=64, db_index=True)
    manufacturing_date = models.DateField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True, db_index=True)
    rack_location = models.ForeignKey(
        RackLocation,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="batches",
        db_index=True,
    )

    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    mrp = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)

    current_stock = models.IntegerField(
        default=0,
        help_text="Updated via purchases, sales and returns."
    )

    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "medicine_batches"
        unique_together = ("medicine", "batch_number")
        indexes = [
            models.Index(fields=["medicine", "batch_number"]),
            models.Index(fields=["expiry_date"]),
            models.Index(fields=["current_stock"]),
        ]

    def __str__(self):
        return f"{self.medicine.name} | {self.batch_number}"


# ==========================
#  Suppliers & Customers
# ==========================

class Supplier(TimeStampedModel):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, db_index=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True, db_index=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    gst_number = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "suppliers"
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["phone"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.name


class Customer(TimeStampedModel):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, db_index=True)
    phone = models.CharField(max_length=20, blank=True, null=True, db_index=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "customers"
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["phone"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.name


# ==========================
#  Purchase (Stock Inward)
# ==========================

class PurchaseInvoice(TimeStampedModel):
    PAYMENT_MODE_CASH = "CASH"
    PAYMENT_MODE_UPI = "UPI"
    PAYMENT_MODE_CARD = "CARD"
    PAYMENT_MODE_CREDIT = "CREDIT"

    PAYMENT_MODE_CHOICES = [
        (PAYMENT_MODE_CASH, "Cash"),
        (PAYMENT_MODE_UPI, "UPI"),
        (PAYMENT_MODE_CARD, "Card"),
        (PAYMENT_MODE_CREDIT, "Credit"),
    ]

    id = models.BigAutoField(primary_key=True)
    invoice_number = models.CharField(
        max_length=64,
        db_index=True,
        help_text="Supplier's invoice number"
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name="purchase_invoices",
        db_index=True,
    )
    invoice_date = models.DateField(default=timezone.now, db_index=True)
    payment_mode = models.CharField(
        max_length=16,
        choices=PAYMENT_MODE_CHOICES,
        default=PAYMENT_MODE_CASH,
        db_index=True,
    )
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    remarks = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="created_purchase_invoices",
    )

    class Meta:
        db_table = "purchase_invoices"
        indexes = [
            models.Index(fields=["invoice_number"]),
            models.Index(fields=["invoice_date"]),
            models.Index(fields=["supplier"]),
        ]


class PurchaseInvoiceItem(models.Model):
    id = models.BigAutoField(primary_key=True)
    purchase_invoice = models.ForeignKey(
        PurchaseInvoice,
        on_delete=models.CASCADE,
        related_name="items",
        db_index=True,
    )
    medicine_batch = models.ForeignKey(
        MedicineBatch,
        on_delete=models.PROTECT,
        related_name="purchase_items",
        db_index=True,
    )
    quantity = models.IntegerField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    mrp = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="purchase_price * quantity"
    )

    class Meta:
        db_table = "purchase_invoice_items"
        indexes = [
            models.Index(fields=["purchase_invoice"]),
            models.Index(fields=["medicine_batch"]),
        ]


# ==========================
#  Sales (Billing / Invoice)
# ==========================

class SalesInvoice(TimeStampedModel):
    STATUS_DRAFT = "DRAFT"
    STATUS_COMPLETED = "COMPLETED"
    STATUS_CANCELLED = "CANCELLED"

    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    PAYMENT_MODE_CASH = "CASH"
    PAYMENT_MODE_UPI = "UPI"
    PAYMENT_MODE_CARD = "CARD"
    PAYMENT_MODE_CREDIT = "CREDIT"

    PAYMENT_MODE_CHOICES = [
        (PAYMENT_MODE_CASH, "Cash"),
        (PAYMENT_MODE_UPI, "UPI"),
        (PAYMENT_MODE_CARD, "Card"),
        (PAYMENT_MODE_CREDIT, "Credit / Borrow"),
    ]

    id = models.BigAutoField(primary_key=True)
    invoice_number = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        help_text="Internal invoice number with prefix"
    )
    invoice_date = models.DateTimeField(default=timezone.now, db_index=True)
    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="sales_invoices",
        db_index=True,
    )
    status = models.CharField(
        max_length=16,
        choices=STATUS_CHOICES,
        default=STATUS_COMPLETED,
        db_index=True,
    )
    payment_mode = models.CharField(
        max_length=16,
        choices=PAYMENT_MODE_CHOICES,
        default=PAYMENT_MODE_CASH,
        db_index=True,
    )
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="total_amount - discount_amount"
    )
    amount_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="If less than net_amount, remaining goes into customer due."
    )
    remarks = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="created_sales_invoices",
    )

    class Meta:
        db_table = "sales_invoices"
        indexes = [
            models.Index(fields=["invoice_number"]),
            models.Index(fields=["invoice_date"]),
            models.Index(fields=["customer"]),
            models.Index(fields=["status"]),
            models.Index(fields=["payment_mode"]),
        ]


class SalesInvoiceItem(models.Model):
    id = models.BigAutoField(primary_key=True)
    sales_invoice = models.ForeignKey(
        SalesInvoice,
        on_delete=models.CASCADE,
        related_name="items",
        db_index=True,
    )
    medicine_batch = models.ForeignKey(
        MedicineBatch,
        on_delete=models.PROTECT,
        related_name="sales_items",
        db_index=True,
    )
    quantity = models.IntegerField()
    mrp = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="selling_price * quantity"
    )

    class Meta:
        db_table = "sales_invoice_items"
        indexes = [
            models.Index(fields=["sales_invoice"]),
            models.Index(fields=["medicine_batch"]),
        ]


# ==========================
#  Borrow / Credit System (Customer Ledger)
# ==========================

class CustomerLedgerEntry(TimeStampedModel):
    """
    Tracks customer borrow/credit and payments.
    Positive amount = customer owes store (debit).
    Negative amount = customer paid (credit).
    """
    ENTRY_TYPE_SALE = "SALE"
    ENTRY_TYPE_PAYMENT = "PAYMENT"
    ENTRY_TYPE_ADJUSTMENT = "ADJUSTMENT"

    ENTRY_TYPE_CHOICES = [
        (ENTRY_TYPE_SALE, "Sale (Invoice)"),
        (ENTRY_TYPE_PAYMENT, "Payment Received"),
        (ENTRY_TYPE_ADJUSTMENT, "Adjustment"),
    ]

    id = models.BigAutoField(primary_key=True)
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="ledger_entries",
        db_index=True,
    )
    sales_invoice = models.ForeignKey(
        SalesInvoice,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="ledger_entries",
        db_index=True,
        help_text="Linked for SALE entries",
    )
    entry_type = models.CharField(
        max_length=16,
        choices=ENTRY_TYPE_CHOICES,
        db_index=True,
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Positive for due, negative for payment."
    )
    remarks = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="customer_ledger_entries",
    )

    class Meta:
        db_table = "customer_ledger_entries"
        indexes = [
            models.Index(fields=["customer"]),
            models.Index(fields=["entry_type"]),
            models.Index(fields=["created_at"]),
        ]


# ==========================
#  Stock Movement (For audit and reports)
# ==========================

class StockMovement(TimeStampedModel):
    """
    Detailed log of stock changes per batch.
    quantity_change: +ve for inward, -ve for outward.
    """

    MOVEMENT_PURCHASE = "PURCHASE"
    MOVEMENT_SALE = "SALE"
    MOVEMENT_RETURN_TO_SUPPLIER = "RETURN_SUPPLIER"
    MOVEMENT_ADJUSTMENT = "ADJUSTMENT"

    MOVEMENT_TYPE_CHOICES = [
        (MOVEMENT_PURCHASE, "Purchase"),
        (MOVEMENT_SALE, "Sale"),
        (MOVEMENT_RETURN_TO_SUPPLIER, "Return to Supplier"),
        (MOVEMENT_ADJUSTMENT, "Adjustment"),
    ]

    id = models.BigAutoField(primary_key=True)
    medicine_batch = models.ForeignKey(
        MedicineBatch,
        on_delete=models.CASCADE,
        related_name="stock_movements",
        db_index=True,
    )
    movement_type = models.CharField(
        max_length=32,
        choices=MOVEMENT_TYPE_CHOICES,
        db_index=True,
    )
    quantity_change = models.IntegerField()
    reference_purchase_invoice = models.ForeignKey(
        PurchaseInvoice,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="stock_movements",
        db_index=True,
    )
    reference_sales_invoice = models.ForeignKey(
        SalesInvoice,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="stock_movements",
        db_index=True,
    )
    remarks = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "stock_movements"
        indexes = [
            models.Index(fields=["medicine_batch"]),
            models.Index(fields=["movement_type"]),
            models.Index(fields=["created_at"]),
        ]


# ==========================
#  Expiry Return to Supplier
# ==========================

class ExpiryReturn(TimeStampedModel):
    id = models.BigAutoField(primary_key=True)
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name="expiry_returns",
        db_index=True,
    )
    return_number = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        help_text="Internal return reference number"
    )
    return_date = models.DateField(default=timezone.now, db_index=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    remarks = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="created_expiry_returns",
    )

    class Meta:
        db_table = "expiry_returns"
        indexes = [
            models.Index(fields=["return_number"]),
            models.Index(fields=["return_date"]),
        ]


class ExpiryReturnItem(models.Model):
    id = models.BigAutoField(primary_key=True)
    expiry_return = models.ForeignKey(
        ExpiryReturn,
        on_delete=models.CASCADE,
        related_name="items",
        db_index=True,
    )
    medicine_batch = models.ForeignKey(
        MedicineBatch,
        on_delete=models.PROTECT,
        related_name="expiry_return_items",
        db_index=True,
    )
    quantity = models.IntegerField()
    rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Rate at which supplier accepts return"
    )
    line_total = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = "expiry_return_items"
        indexes = [
            models.Index(fields=["expiry_return"]),
            models.Index(fields=["medicine_batch"]),
        ]

