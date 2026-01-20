import os
import pdfkit
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from apps.models import SalesInvoice, SalesInvoiceItem, StoreProfile, MedicineInventory

class InvoiceGenerate(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        invoice_db_id = request.data.get('invoice_id')
        
        try:
            invoice = SalesInvoice.objects.get(id=invoice_db_id)
            items = SalesInvoiceItem.objects.filter(sales_invoice_id=invoice.id)
            store = StoreProfile.objects.first()
            
            # Construct Absolute Path for Signature
            # This points to your project_root/media/signature/sign.jpeg
            sig_path = os.path.join(settings.MEDIA_ROOT, 'signature', 'sign.jpeg')
            
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

            context = {
                'invoice': invoice,
                'items': enriched_items,
                'store': store,
                'logo_url': request.build_absolute_uri(store.logo.url) if store.logo else None,
                'signature_path': sig_path, # Pass the absolute path here
            }

            html_content = render_to_string('invoices/invoice_template.html', context)

            options = {
                'page-size': 'A4',
                'margin-top': '0.5in',
                'margin-right': '0.5in',
                'margin-bottom': '0.5in',
                'margin-left': '0.5in',
                'encoding': "UTF-8",
                'enable-local-file-access': None # Required to read signature_path
            }
            
            config = pdfkit.configuration(wkhtmltopdf=settings.PATH_WKHTMLTOPDF)
            pdf = pdfkit.from_string(html_content, False, options=options, configuration=config)

            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="Invoice_{invoice.invoice_id}.pdf"'
            return response

        except Exception as e:
            return JsonResponse({'status': False, 'message': str(e)}, status=500)