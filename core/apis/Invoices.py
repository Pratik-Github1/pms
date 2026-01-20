import pdfkit
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from apps.models import SalesInvoice, SalesInvoiceItem, StoreProfile, MedicineInventory

class InvoiceGenerate(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        invoice_db_id = request.data.get('invoice_id') # This is the primary key (id)
        
        try:
            # 1. Fetch Data
            invoice = SalesInvoice.objects.get(id=invoice_db_id)
            items = SalesInvoiceItem.objects.filter(sales_invoice_id=invoice.id)
            store = StoreProfile.objects.first() # Get the single store record
            
            # Enrich items with medicine names from MedicineInventory
            enriched_items = []
            for item in items:
                med = MedicineInventory.objects.filter(id=item.medicine_id).first()
                enriched_items.append({
                    'name': med.name if med else "Unknown Medicine",
                    'qty': item.quantity,
                    'mrp': item.mrp,
                    'discount': item.discount,
                    'selling_price': item.selling_price
                })

            # 2. Context for Template
            context = {
                'invoice': invoice,
                'items': enriched_items,
                'store': store,
                'logo_url': request.build_absolute_uri(store.logo.url) if store.logo else None
            }

            # 3. Render HTML to String
            html_content = render_to_string('invoices/invoice_template.html', context)

            # 4. PDFKit Configuration
            options = {
                'page-size': 'A4',
                'margin-top': '0.75in',
                'margin-right': '0.75in',
                'margin-bottom': '0.75in',
                'margin-left': '0.75in',
                'encoding': "UTF-8",
                'enable-local-file-access': None
            }
            
            # Use the path from your settings.py
            config = pdfkit.configuration(wkhtmltopdf=settings.PATH_WKHTMLTOPDF)
            
            # 5. Generate PDF
            pdf = pdfkit.from_string(html_content, False, options=options, configuration=config)

            # 6. Return Response
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="Invoice_{invoice.invoice_id}.pdf"'
            return response

        except SalesInvoice.DoesNotExist:
            return JsonResponse({'status': False, 'message': 'Invoice not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': False, 'message': str(e)}, status=500)