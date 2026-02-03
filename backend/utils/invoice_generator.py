from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY
from reportlab.lib import colors
from datetime import datetime
import os
from pathlib import Path
import requests
from io import BytesIO

INVOICE_DIR = Path("/app/backend/invoices")
INVOICE_DIR.mkdir(exist_ok=True)

# Coffee color scheme
COFFEE_DARK = colors.HexColor('#6F4E37')
COFFEE_MEDIUM = colors.HexColor('#8D6E63')
COFFEE_LIGHT = colors.HexColor('#D7CCC8')
CREAM = colors.HexColor('#F5E6D3')
HEADER_BG = colors.HexColor('#3E2723')

def download_logo():
    """Download and cache the BigBean Cafe logo"""
    logo_path = INVOICE_DIR / "bigbean_logo.png"
    if not logo_path.exists():
        try:
            logo_url = "https://customer-assets.emergentagent.com/job_bigbean-system/artifacts/cg0dat1r_BBC-Logo.png"
            response = requests.get(logo_url, timeout=10)
            if response.status_code == 200:
                with open(logo_path, 'wb') as f:
                    f.write(response.content)
        except Exception as e:
            print(f"Could not download logo: {e}")
            return None
    return str(logo_path) if logo_path.exists() else None

def generate_invoice_pdf(invoice_data: dict, company_settings: dict) -> str:
    """
    Generate professional invoice PDF with logo and return the file path
    """
    
    filename = f"BBC-INV-{invoice_data['invoice_number']}.pdf"
    filepath = INVOICE_DIR / filename
    
    # Create PDF with margins
    doc = SimpleDocTemplate(
        str(filepath), 
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=15*mm,
        bottomMargin=20*mm
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=HEADER_BG,
        spaceAfter=5,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=COFFEE_MEDIUM,
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=HEADER_BG,
        spaceAfter=8,
        spaceBefore=12,
        fontName='Helvetica-Bold',
        borderWidth=0,
        borderColor=COFFEE_DARK,
        borderPadding=5
    )
    
    info_label_style = ParagraphStyle(
        'InfoLabel',
        parent=styles['Normal'],
        fontSize=9,
        textColor=COFFEE_MEDIUM,
        fontName='Helvetica-Bold'
    )
    
    info_value_style = ParagraphStyle(
        'InfoValue',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.black
    )
    
    # Add logo and company header
    logo_path = download_logo()
    if logo_path and os.path.exists(logo_path):
        try:
            logo = Image(logo_path, width=0.8*inch, height=0.8*inch)
            logo.hAlign = 'CENTER'
            story.append(logo)
            story.append(Spacer(1, 0.1*inch))
        except:
            pass
    
    # Company Name
    story.append(Paragraph(company_settings.get('company_name', 'BigBeanCafe'), title_style))
    
    # Company details
    company_info = f"""
    <para alignment="center">
    {company_settings.get('company_address', 'Franchise Head Office, India')}<br/>
    Phone: {company_settings.get('company_phone', '+91 1234567890')} | 
    Email: {company_settings.get('company_email', 'info@bigbeancafe.in')}<br/>
    <b>GSTIN:</b> {company_settings.get('company_gstin', '22AAAAA0000A1Z5')}
    </para>
    """
    story.append(Paragraph(company_info, subtitle_style))
    
    # Horizontal line
    story.append(Spacer(1, 0.1*inch))
    line_table = Table([['']], colWidths=[7*inch])
    line_table.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,0), 2, COFFEE_DARK),
    ]))
    story.append(line_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Invoice header section
    invoice_header = [
        [
            Paragraph('<font size=18 color=#6F4E37><b>TAX INVOICE</b></font>', styles['Normal']),
            ''
        ]
    ]
    invoice_header_table = Table(invoice_header, colWidths=[3.5*inch, 3.5*inch])
    invoice_header_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CREAM),
        ('PADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(invoice_header_table)
    story.append(Spacer(1, 0.15*inch))
    
    # Invoice details and customer details in two columns
    invoice_date_formatted = invoice_data['invoice_date'].strftime('%d-%B-%Y')
    
    details_data = [
        [
            Paragraph('<b>Invoice Details:</b>', heading_style),
            Paragraph('<b>Bill To:</b>', heading_style)
        ],
        [
            Paragraph(f"<b>Invoice No:</b> {invoice_data['invoice_number']}", info_value_style),
            Paragraph(f"<b>{invoice_data['franchise_name']}</b>", info_value_style)
        ],
        [
            Paragraph(f"<b>Invoice Date:</b> {invoice_date_formatted}", info_value_style),
            Paragraph(f"{invoice_data.get('franchise_address', '')}", info_value_style)
        ],
        [
            Paragraph(f"<b>Order ID:</b> {invoice_data['order_id'][:20]}...", info_value_style),
            Paragraph(f"<b>GSTIN:</b> {invoice_data.get('franchise_gstin', 'N/A')}", info_value_style)
        ]
    ]
    
    details_table = Table(details_data, colWidths=[3.5*inch, 3.5*inch])
    details_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), COFFEE_LIGHT),
        ('BACKGROUND', (1,0), (1,0), COFFEE_LIGHT),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOX', (0,0), (-1,-1), 1, COFFEE_LIGHT),
        ('GRID', (0,1), (-1,-1), 0.5, COFFEE_LIGHT),
    ]))
    story.append(details_table)
    story.append(Spacer(1, 0.25*inch))
    
    # Items table header
    story.append(Paragraph('<b>Order Details:</b>', heading_style))
    story.append(Spacer(1, 0.1*inch))
    
    # Items Table with SGST/CGST
    table_data = [
        [
            Paragraph('<b>#</b>', info_label_style),
            Paragraph('<b>Product Description</b>', info_label_style),
            Paragraph('<b>Qty</b>', info_label_style),
            Paragraph('<b>Rate (₹)</b>', info_label_style),
            Paragraph('<b>Taxable Amt (₹)</b>', info_label_style),
            Paragraph('<b>SGST (%)</b>', info_label_style),
            Paragraph('<b>SGST (₹)</b>', info_label_style),
            Paragraph('<b>CGST (%)</b>', info_label_style),
            Paragraph('<b>CGST (₹)</b>', info_label_style),
            Paragraph('<b>Total (₹)</b>', info_label_style)
        ]
    ]
    
    for idx, item in enumerate(invoice_data['items'], 1):
        sgst_percent = item.get('sgst_percent', item['gst_percent'] / 2)
        cgst_percent = item.get('cgst_percent', item['gst_percent'] / 2)
        sgst_amount = item.get('sgst_amount', item['gst_amount'] / 2)
        cgst_amount = item.get('cgst_amount', item['gst_amount'] / 2)
        
        table_data.append([
            Paragraph(str(idx), info_value_style),
            Paragraph(item['product_name'], info_value_style),
            Paragraph(str(item['quantity']), info_value_style),
            Paragraph(f"{item['unit_price']:.2f}", info_value_style),
            Paragraph(f"{item['taxable_amount']:.2f}", info_value_style),
            Paragraph(f"{sgst_percent:.1f}%", info_value_style),
            Paragraph(f"{sgst_amount:.2f}", info_value_style),
            Paragraph(f"{cgst_percent:.1f}%", info_value_style),
            Paragraph(f"{cgst_amount:.2f}", info_value_style),
            Paragraph(f"<b>{item['total_amount']:.2f}</b>", info_value_style)
        ])
    
    # Create table with column widths
    col_widths = [0.3*inch, 2*inch, 0.4*inch, 0.6*inch, 0.8*inch, 0.5*inch, 0.6*inch, 0.5*inch, 0.6*inch, 0.7*inch]
    
    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        # Header styling
        ('BACKGROUND', (0, 0), (-1, 0), HEADER_BG),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        
        # Data rows
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Serial number
        ('ALIGN', (2, 1), (-1, -1), 'CENTER'),  # Numbers aligned center
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),  # Product name left
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('PADDING', (0, 1), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, CREAM]),
        
        # Grid
        ('GRID', (0, 0), (-1, -1), 0.5, COFFEE_MEDIUM),
        ('BOX', (0, 0), (-1, -1), 1.5, COFFEE_DARK),
        
        # Valign
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 0.2*inch))
    
    # Totals section
    sgst_total = invoice_data.get('sgst_total', invoice_data['gst_total'] / 2)
    cgst_total = invoice_data.get('cgst_total', invoice_data['gst_total'] / 2)
    
    totals_data = [
        ['', 'Subtotal:', f"₹ {invoice_data['subtotal']:,.2f}"],
        ['', 'SGST Total:', f"₹ {sgst_total:,.2f}"],
        ['', 'CGST Total:', f"₹ {cgst_total:,.2f}"],
        ['', 'Total Tax:', f"₹ {invoice_data['gst_total']:,.2f}"],
        ['', 'Grand Total:', f"₹ {invoice_data['grand_total']:,.2f}"],
    ]
    
    totals_table = Table(totals_data, colWidths=[3.8*inch, 1.8*inch, 1.4*inch])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('FONTNAME', (1, 0), (1, -2), 'Helvetica-Bold'),
        ('FONTNAME', (1, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (1, -1), (-1, -1), 12),
        ('TEXTCOLOR', (1, -1), (-1, -1), COFFEE_DARK),
        ('BACKGROUND', (1, -1), (-1, -1), CREAM),
        ('PADDING', (1, 0), (-1, -1), 8),
        ('LINEABOVE', (1, -1), (-1, -1), 2, COFFEE_DARK),
        ('BOX', (1, 0), (-1, -1), 1, COFFEE_LIGHT),
    ]))
    
    story.append(totals_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Amount in words
    amount_words = number_to_words(invoice_data['grand_total'])
    story.append(Paragraph(f'<b>Amount in Words:</b> {amount_words}', info_value_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Terms and conditions
    terms_style = ParagraphStyle(
        'Terms',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        leading=12
    )
    
    story.append(Paragraph('<b>Terms & Conditions:</b>', heading_style))
    terms = """
    1. This is a computer-generated invoice and does not require a physical signature.<br/>
    2. Credit amount has been deducted from your available credit limit upon order approval.<br/>
    3. Payment is due when credit limit is exhausted. Fixed payment amount: ₹1,00,000.<br/>
    4. All disputes are subject to jurisdiction at the company's registered office location.<br/>
    5. Goods once sold will not be taken back or exchanged.<br/>
    """
    story.append(Paragraph(terms, terms_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Footer with branding
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=COFFEE_MEDIUM,
        alignment=TA_CENTER
    )
    
    story.append(Spacer(1, 0.2*inch))
    footer_line = Table([['']], colWidths=[7*inch])
    footer_line.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,0), 1, COFFEE_LIGHT),
    ]))
    story.append(footer_line)
    story.append(Spacer(1, 0.1*inch))
    
    footer_text = f"""
    <para alignment="center">
    <b>Thank you for your business!</b><br/>
    BigBeanCafe Franchise Ordering System | www.bigbeancafe.in<br/>
    For any queries, contact: {company_settings.get('company_email', 'info@bigbeancafe.in')} | 
    {company_settings.get('company_phone', '+91 1234567890')}
    </para>
    """
    story.append(Paragraph(footer_text, footer_style))
    
    # Build PDF
    doc.build(story)
    
    return str(filepath)

def number_to_words(num):
    """Convert number to words (Indian system)"""
    try:
        num = float(num)
        rupees = int(num)
        paise = int(round((num - rupees) * 100))
        
        def convert_to_words(n):
            if n == 0:
                return "Zero"
            
            ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"]
            tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
            teens = ["Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
            
            if n < 10:
                return ones[n]
            elif n < 20:
                return teens[n - 10]
            elif n < 100:
                return tens[n // 10] + (" " + ones[n % 10] if n % 10 != 0 else "")
            elif n < 1000:
                return ones[n // 100] + " Hundred" + (" and " + convert_to_words(n % 100) if n % 100 != 0 else "")
            elif n < 100000:
                return convert_to_words(n // 1000) + " Thousand" + (" " + convert_to_words(n % 1000) if n % 1000 != 0 else "")
            elif n < 10000000:
                return convert_to_words(n // 100000) + " Lakh" + (" " + convert_to_words(n % 100000) if n % 100000 != 0 else "")
            else:
                return convert_to_words(n // 10000000) + " Crore" + (" " + convert_to_words(n % 10000000) if n % 10000000 != 0 else "")
        
        result = "Rupees " + convert_to_words(rupees)
        if paise > 0:
            result += " and " + convert_to_words(paise) + " Paise"
        result += " Only"
        return result
    except:
        return "Amount conversion error"

def get_next_invoice_number(year: int) -> str:
    """
    Generate next invoice number in format: YYYY-MMDDHHMMSS
    """
    return f"{year}-{datetime.now().strftime('%m%d%H%M%S')}"
