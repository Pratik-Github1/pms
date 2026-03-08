# Panda Medicine Store (PMS) — Project Summary

> **Project Name:** PANDA MEDICINES STORE  
> **Framework:** Django 5.2.6 + Django REST Framework 3.16.0  
> **Database:** MySQL (`medicine_store_db`, port 3307, user `root`)  
> **Python Virtual Environment:** `C:\Projects\env\`  
> **Settings Module:** `app.settings`  
> **Run Command:** `run_shop.bat` (activates venv → `runserver` → opens Chrome)

---

## 1. High-Level Architecture

```
pms-v1/
├── app/               # Django project config (settings, root urls, wsgi, asgi)
├── apps/              # Frontend views (template rendering) + ORM models + helpers
├── core/              # REST API layer (all business logic lives here)
├── templates/         # Django HTML templates (base layout + page templates)
├── content/assets/    # Static assets (CSS, JS, vendor libs, images)
├── media/             # User-uploaded files (store logos, signatures)
├── scripts/           # SQL scripts (table definitions, seed data)
├── secrets/           # Environment-specific secret files (.env.local.secrets, etc.)
├── manage.py
├── requirements.txt
└── run_shop.bat
```

### Two Django Apps

| App    | Purpose |
|--------|---------|
| `apps` | **Frontend + Models + Helpers.** Serves HTML pages via function-based views. Contains all Django ORM models. Houses utility helpers (validators, JWT auth, permissions, exception handling). |
| `core` | **REST API layer.** All API views (class-based `APIView`s) live here under `core/apis/`. Authentication endpoints also live under `core/authentication/`. |

---

## 2. URL Routing

### Root (`app/urls.py`)
| Prefix    | Target            |
|-----------|-------------------|
| `admin/`  | Django Admin      |
| `""`      | `apps.urls` (frontend pages) |
| `apis/`   | `core.urls` (REST APIs)      |

### Frontend Pages (`apps/urls.py`, namespace: `apps`)
| URL                   | View Function              | Template                            |
|-----------------------|----------------------------|-------------------------------------|
| `/`                   | `DashboardPage`            | `dashboard/dash.html`               |
| `/loginPage/`         | `LoginPage`                | `auth/login.html`                   |
| `/registerPage/`      | `RegisterPage`             | `auth/register.html`                |
| `/profile/`           | `StoreProfilePage`         | `store_profile/store_profile.html`  |
| `/addMedicine/`       | `addMedicinePage`          | `medicines/add_medicine.html`       |
| `/medicineList/`      | `medicineListPage`         | `medicines/medicine_list.html`      |
| `/addSupplier/`       | `addSupplierPage`          | `purchases/add_supplier.html`       |
| `/supplierList/`      | `supplierListPage`         | `purchases/supplier_list.html`      |
| `/createPurchaseNote/`| `createPurchaseNotePage`   | `purchases/create_purchase_note.html` |
| `/purchaseNoteList/`  | `purchaseNoteListPage`     | `purchases/purchase_note_list.html` |
| `/createSalesNote/`   | `createSalesInvoicePage`   | `sales/create_sales_note.html`      |
| `/salesInvoiceList/`  | `sales_invoice_list_page`  | `sales/sales_note_list.html`        |

### REST APIs (`core/urls.py`, namespace: `core`, prefix: `/apis/`)
| Endpoint                    | View Class                         | Methods         |
|-----------------------------|------------------------------------|-----------------|
| `signup`                    | `OwnerSignupView`                  | POST            |
| `login`                     | `LoginView`                        | POST            |
| `generateAccessToken`       | `GenerateAccessToken`              | POST            |
| `logout`                    | `UserLogoutView`                   | POST            |
| `getStoreInformation`       | `GETStoreProfileInformation`       | GET             |
| `storeInformation`          | `StoreProfileCRUDView`             | POST/GET/PATCH/DELETE |
| `medicines`                 | `MedicineCRUDView`                 | POST/GET/PATCH  |
| `medicineList`              | `MedicineInventoryListView`        | GET (paginated) |
| `getMedicines`              | `GetMedicineInventoryListSmall`    | GET (lightweight) |
| `supplierList`              | `SupplierListView`                 | GET (paginated) |
| `getSuppliers`              | `GetSupplierListSmall`             | GET (lightweight) |
| `suppliers`                 | `SupplierCRUDView`                 | POST/GET/PATCH/DELETE |
| `purchaseInvoices`          | `PurchaseInvoiceCRUDView`          | POST/GET/PATCH  |
| `purchaseInvoicesList`      | `PurchaseInvoiceListView`          | GET (paginated) |
| `salesInvoices`             | `SalesInvoiceCRUDView`             | POST/GET/PATCH  |
| `salesInvoicesList`         | `SalesInvoiceListView`             | GET (paginated) |
| `generateInvoice`           | `InvoiceGenerate`                  | POST (PDF)      |

---

## 3. Database Models (`apps/models.py`)

All models use `managed = True` (except `BlacklistedToken` which is `managed = False`).  
**Foreign keys are stored as `BigIntegerField` (manual FK, not Django ForeignKey).**

| Model                  | Table Name               | Key Fields |
|------------------------|--------------------------|------------|
| `Users`                | `users`                  | username, password (hashed), full_name, mobile_number, email, role (OWNER/CASHIER/STOCK_MANAGER/VIEWER), is_active, last_login |
| `BlacklistedToken`     | `blacklisted_token`      | token, blacklisted_at. **managed=False** |
| `StoreProfile`         | `store_profile`          | store_name, owner_name, gst_number, drug_license_number, city/state/pincode/country, address_line, invoice_prefix, invoice_footer_note, logo |
| `MedicineInventory`    | `medicine_inventory`     | name, medicine_uses, hsn_code, unit, packing_details, low_stock_alert, batch_number, manufacturing_date, expiry_date, rack_location, purchase_price, mrp, current_stock, is_active, is_expired |
| `Supplier`             | `suppliers`              | name, company_name, phone, email, address, gst_number, is_active |
| `PurchaseInvoice`      | `purchase_invoices`      | supplier_id, invoice_number, invoice_date, payment_mode, total_amount, amount_paid, remarks |
| `PurchaseInvoiceItem`  | `purchase_invoice_items` | purchase_invoice_id, medicine_id, quantity, purchase_price, mrp |
| `SalesInvoice`         | `sales_invoices`         | invoice_id (auto-generated: PMS-YYYYMMDD-RANDOM), invoice_date, payment_mode, customer_name, doctor_name, total_medicines, total_price, total_discount_price, final_selling_price |
| `SalesInvoiceItem`     | `sales_invoice_items`    | sales_invoice_id, medicine_id, quantity, mrp, discount, discount_price, selling_price |
| `ExpiryReturn`         | `expiry_returns`         | supplier_id, return_number, return_date, total_amount, remarks, is_returned |
| `ExpiryReturnItem`     | `expiry_return_items`    | expiry_return_id, medicine_id, batch_number, quantity, rate |

---

## 4. Authentication & Security

### JWT Authentication (Custom, NOT Django's default auth)
- **Library:** `PyJWT` (manual encode/decode) + `djangorestframework-simplejwt` config
- **Custom Auth Class:** `apps.helpers.simpleJWT_helper.CustomUserAuthentication`
  - Reads `Authorization: Bearer <token>` header
  - Checks `BlacklistedToken` table to reject revoked tokens
  - Decodes JWT using `HS256` and retrieves `Users` object by `user_id`
- **Token Lifetime:** Access = 7 days, Refresh = 90 days
- **Token Generation:** `core/authentication/auth.py → generate_user_token()` and `apps/helpers/generate_token_helper.py → generate_user_token()`

### Auth Endpoints
- **Signup:** `POST /apis/signup` — Creates owner account with validated name, email, mobile, password
- **Login:** `POST /apis/login` — Validates credentials, returns access + refresh tokens
- **Refresh:** `POST /apis/generateAccessToken` — Re-issues access token from refresh token
- **Logout:** `POST /apis/logout` — Blacklists both access and refresh tokens

### App Signature Permission (HMAC)
- `apps/helpers/permission_helper.py → HasValidAppSignature`
- Validates `X-APP-ID`, `X-APP-TIMESTAMP`, `X-APP-NONCE`, `X-APP-SIGNATURE` headers
- Uses HMAC-SHA256 with a 5-minute time window

---

## 5. Helpers (`apps/helpers/`)

| File                       | Purpose |
|----------------------------|---------|
| `general_helper.py`        | Validators: `validate_mobile_number()`, `validate_email_address()`, `validate_password()`, `validate_full_name()` |
| `simpleJWT_helper.py`      | `CustomUserAuthentication` — DRF authentication backend using JWT |
| `generate_token_helper.py` | `generate_user_token()` — builds JWT payloads with role-based fields |
| `permission_helper.py`     | `HasValidAppSignature` — HMAC-based permission class, `AccessDeniedException` |
| `exception_handler.py`     | `custom_exception_handler()` — Global DRF exception handler (401/403 formatting, browser redirect) |

---

## 6. API Modules (`core/apis/`)

| File                      | Classes | Functionality |
|---------------------------|---------|---------------|
| `Medicine.py`             | `MedicineCRUDView`, `MedicineInventoryListView`, `GetMedicineInventoryListSmall` | CRUD for medicine inventory; paginated list with search; lightweight dropdown list |
| `Supplier.py`             | `SupplierCRUDView`, `SupplierListView`, `GetSupplierListSmall` | CRUD for suppliers; paginated list with search; lightweight dropdown list |
| `Purchases.py`            | `PurchaseInvoiceCRUDView`, `PurchaseInvoiceListView` | CRUD for purchase invoices (with line items); updates medicine stock on creation; paginated list |
| `Sales.py`                | `SalesInvoiceCRUDView`, `SalesInvoiceListView` | CRUD for sales invoices (with line items); deducts medicine stock; paginated list |
| `StoreInformations.py`    | `StoreProfileCRUDView`, `GETStoreProfileInformation` | CRUD for store profile; public GET for store info |
| `Invoices.py`             | `InvoiceGenerate` | Generates PDF invoice using `pdfkit` + `wkhtmltopdf` from sales invoice data |
| `ExpiryReturn.py`         | `ExpiryReturnCRUDView`, `ExpiryReturnItemCRUDView` | CRUD for expiry returns and return line items |

---

## 7. Templates

- **Base Layout:** `templates/base.html` — Sidebar navigation + content block
  - Uses Bootstrap-based admin theme (vendor CSS/JS from `content/assets/`)
  - Sidebar: Dashboard, Store Profile, Medicines, Purchases, Sales, Expires
- **Auth:** `templates/auth/` — `login.html`, `register.html`, `signup.html`
- **Dashboard:** `templates/dashboard/dash.html`
- **Store Profile:** `templates/store_profile/store_profile.html`
- **Medicines:** `templates/medicines/` — `add_medicine.html`, `medicine_list.html`
- **Purchases:** `templates/purchases/` — `add_supplier.html`, `supplier_list.html`, `create_purchase_note.html`, `purchase_note_list.html`
- **Sales:** `templates/sales/` — `create_sales_note.html`, `sales_note_list.html`
- **Invoices:** `templates/invoices/invoice_template.html` — HTML template for PDF generation

---

## 8. Environment Configuration

- `.env` → contains `ENV_TYPE` (local / preproduction / production)
- `secrets/.env.local.secrets` → `SECRET_KEY`, `DEBUG`, and other env-specific secrets
- Secrets folder is gitignored

---

## 9. Key Dependencies (`requirements.txt`)

| Package                        | Version  | Purpose |
|--------------------------------|----------|---------|
| Django                         | 5.2.6    | Web framework |
| djangorestframework            | 3.16.0   | REST API framework |
| djangorestframework-simplejwt  | 5.5.0    | JWT config (mostly unused — custom JWT is primary) |
| mysqlclient                    | 2.2.7    | MySQL database adapter |
| PyJWT                          | 2.9.0    | Manual JWT encode/decode |
| pdfkit                         | 1.0.0    | PDF generation |
| pillow                         | 11.2.1   | Image handling (logo upload) |
| python-dotenv                  | 1.1.0    | Load .env files |

---

## 10. Static & Media Files

- **Static files root:** `content/` (served at `/static/`)
- **Static assets:** `content/assets/` — vendors (Bootstrap, jQuery, Font Awesome, MDI, Themify Icons), custom CSS/JS
- **Media root:** `media/` (served at `/media/`) — store logos, signatures

---

## 11. Database Notes

- **Engine:** MySQL on `localhost:3307`
- **DB Name:** `medicine_store_db`
- **SQL Mode:** `STRICT_TRANS_TABLES`
- **Table creation scripts:** `scripts/tables.sql` and `scripts/medicine_store_db.sql`
- **All FKs are manual** (BigIntegerField, not Django ForeignKey) — no cascading deletes at ORM level
- **Migrations are gitignored** — tables are managed via raw SQL scripts

---

## 12. Business Domain Summary

This is a **Pharmacy Management System** for a single medicine store. Key workflows:

1. **Store Setup** — Owner registers → configures store profile (name, GST, license, logo)
2. **Medicine Inventory** — Add medicines with batch number, expiry, rack location, stock, pricing
3. **Supplier Management** — Add/manage medicine suppliers with contact & GST details
4. **Purchase Flow** — Create purchase invoices from suppliers → links medicine items → updates stock (+)
5. **Sales Flow** — Create sales invoices for customers → add medicines with discount → updates stock (−) → auto-generates invoice ID (PMS-YYYYMMDD-XXXXX)
6. **Invoice PDF** — Generate downloadable PDF invoices from sales data using `wkhtmltopdf`
7. **Expiry Returns** — Track and return expired medicines to suppliers

---

## 13. Important Patterns & Conventions

- **API Response Format:** `{"status": true/false, "message": "...", "data": {...}}`
- **Pagination:** `PageNumberPagination` with `page_size=10`, max=100
- **Error Handling:** Global `custom_exception_handler` formats all DRF exceptions
- **No Django ForeignKey:** All relationships use `BigIntegerField` with manual joins
- **Template Pattern:** All pages extend `base.html` and define `{% block content %}`
- **Frontend ↔ API:** Templates call APIs via JavaScript (fetch/AJAX) to `/apis/` endpoints
- **Timezone:** `Asia/Kolkata`, `USE_TZ=False`
