import random
import datetime
from django.db import models

class Users(models.Model):
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

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

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

class StoreProfile(models.Model):
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

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "store_profile"

class MedicineInventory(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    medicine_uses = models.TextField(blank=True, null=True)
    hsn_code = models.CharField(max_length=20, blank=True, null=True, help_text="For GST or future tax support")

    UNIT_CHOICES = (
        ("strip", "Strip"),
        ("bottle", "Bottle"),
        ("tube", "Tube"),
        ("vial", "Vial"),
        ("other", "Other"),
    )
    unit = models.CharField(max_length=32, choices=UNIT_CHOICES, default="strip")
    packing_details = models.CharField(max_length=128, blank=True, null=True, help_text="e.g., 10 tablets per strip")
    low_stock_alert = models.IntegerField(default=0, help_text="Alert if stock falls below this level")
    batch_number = models.CharField(max_length=128, db_index=True)
    manufacturing_date = models.DateField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True, db_index=True)
    rack_location = models.CharField(max_length=64, db_index=True, blank=True, null=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    mrp = models.DecimalField(max_digits=10, decimal_places=2)
    current_stock = models.IntegerField(default=0, help_text="Updated via purchases, sales and returns")
    is_active = models.BooleanField(default=True, db_index=True)
    is_expired = models.BooleanField(default=False, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "medicine_inventory"
        indexes = [
            models.Index(fields=["name"], name="idx_med_inv_name"),
            models.Index(fields=["name", "batch_number"], name="idx_med_inv_name_batch"),
            models.Index(fields=["expiry_date"], name="idx_med_inv_expiry"),
            models.Index(fields=["current_stock"], name="idx_med_inv_stock"),
            models.Index(fields=["is_active"], name="idx_med_inv_active"),
            models.Index(fields=["is_active", "expiry_date"], name="idx_med_inv_active_expiry"),
            models.Index(fields=["is_active", "current_stock"], name="idx_med_inv_active_stock"),
            models.Index(fields=["rack_location"], name="idx_med_inv_rack"),
            models.Index(fields=["expiry_date"], name="idx_med_expiry"),
            models.Index(fields=["created_at"], name="idx_med_created_at"),
        ]

class Supplier(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, db_index=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True, db_index=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    gst_number = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "suppliers"
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["phone"]),
            models.Index(fields=["is_active"]),
        ]

class PurchaseInvoice(models.Model):
    supplier_id = models.BigIntegerField(db_index=True)
    invoice_number = models.CharField(max_length=64, db_index=True, help_text="Supplier's invoice number")
    invoice_date = models.DateField(db_index=True)
    payment_mode = models.CharField(max_length=16, default="Cash")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    remarks = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "purchase_invoices"
        indexes = [
            models.Index(fields=["supplier_id"]),
            models.Index(fields=["invoice_number"]),
            models.Index(fields=["invoice_date"])
        ]

class PurchaseInvoiceItem(models.Model):
    purchase_invoice_id = models.BigIntegerField(db_index=True)
    medicine_id = models.BigIntegerField(db_index=True)
    quantity = models.IntegerField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    mrp = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "purchase_invoice_items"
        indexes = [
            models.Index(fields=["purchase_invoice_id"], name="idx_pi_item_pi"),
            models.Index(fields=["medicine_id"], name="idx_pi_item_med"),
        ]

class SalesInvoice(models.Model):
    invoice_id = models.CharField(max_length=64, db_index=True, unique=True)
    invoice_date = models.DateTimeField(db_index=True, auto_now_add=True)
    payment_mode = models.CharField(max_length=16)
    customer_name = models.CharField(max_length=255, blank=True, null=True)
    doctor_name = models.CharField(max_length=255, blank=True, null=True)

    total_medicines = models.IntegerField(default=0)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_discount_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    final_selling_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sales_invoices"
        indexes = [
            models.Index(fields=["invoice_id"], name="idx_si_id"),
            models.Index(fields=["invoice_date"], name="idx_si_date"),
            models.Index(fields=["invoice_id", "invoice_date"], name="idx_si_id_date"),
        ]
    def save(self, *args, **kwargs):
        if not self.invoice_id:
            self.invoice_id = self.generate_invoice_id()
        super(SalesInvoice, self).save(*args, **kwargs)

    def generate_invoice_id(self):
        """
        Generates a unique ID: PMS-YYYYMMDD-RANDOM
        Example: PMS-20231027-84291
        """
        date_str = datetime.datetime.now().strftime('%Y%m%d')
        # Generate a random 5-digit integer
        random_bits = random.randint(10000, 99999)
        new_id = f"PMS-{date_str}-{random_bits}"
        
        # Double check uniqueness in the database
        while SalesInvoice.objects.filter(invoice_id=new_id).exists():
            random_bits = random.randint(10000, 99999)
            new_id = f"PMS-{date_str}-{random_bits}"
            
        return new_id

class SalesInvoiceItem(models.Model):
    sales_invoice_id = models.BigIntegerField(db_index=True)
    medicine_id = models.BigIntegerField(db_index=True)
    quantity = models.IntegerField(default=1)
    mrp = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.IntegerField(default=10)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sales_invoice_items"
        indexes = [
            models.Index(fields=["sales_invoice_id"], name="idx_sii_si"),
            models.Index(fields=["medicine_id"], name="idx_sii_med"),
        ]

class ExpiryReturn(models.Model):
    supplier_id = models.BigIntegerField(db_index=True)
    return_number = models.CharField(max_length=64, unique=True, db_index=True, help_text="Internal return reference number")
    return_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    remarks = models.TextField(blank=True, null=True)
    is_returned = models.BooleanField(default=False, db_index=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "expiry_returns"
        indexes = [
            models.Index(fields=["supplier_id"], name="idx_er_supplier"),
            models.Index(fields=["return_number"], name="idx_er_number"),
            models.Index(fields=["is_returned"], name="idx_er_returned"),
        ]

class ExpiryReturnItem(models.Model):
    id = models.BigAutoField(primary_key=True)
    expiry_return_id = models.BigIntegerField(db_index=True)
    medicine_id = models.BigIntegerField(db_index=True)
    batch_number = models.CharField(max_length=128, blank=True, null=True)
    quantity = models.IntegerField()
    rate = models.DecimalField(max_digits=10, decimal_places=2,help_text="Rate at which supplier accepts return")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "expiry_return_items"
        indexes = [
            models.Index(fields=["expiry_return_id"], name="idx_er_item_er"),
            models.Index(fields=["medicine_id"], name="idx_er_item_med"),
        ]

