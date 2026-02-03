from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib import colors
from datetime import datetime
import os
from pathlib import Path
import requests

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
    Generate professional invoice PDF with logo in corner
    """
    
    filename = f"BBC-INV-{invoice_data['invoice_number']}.pdf"
    filepath = INVOICE_DIR / filename
    
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
    company_name_style = ParagraphStyle(
        'CompanyName',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=HEADER_BG,
        spaceAfter=3,
        fontName='Helvetica-Bold',
        alignment=TA_LEFT
    )
    
    company_info_style = ParagraphStyle(
        'CompanyInfo',
        parent=styles['Normal'],
        fontSize=9,
        textColor=COFFEE_MEDIUM,
        leading=12,
        alignment=TA_LEFT
    )
    
    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=11,
        textColor=HEADER_BG,
        spaceAfter=8,
        spaceBefore=10,
        fontName='Helvetica-Bold'
    )
    
    info_value_style = ParagraphStyle(
        'InfoValue',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.black,
        leading=12
    )
    
    # Header with logo in top-right corner
    logo_path = download_logo()
    
    header_data = []
    if logo_path and os.path.exists(logo_path):
        try:
            logo = Image(logo_path, width=1*inch, height=1*inch)
            
            company_info_text = f"""
            <b><font size=24 color=#3E2723>{company_settings.get('company_name', 'BigBeanCafe')}</font></b><br/>
            {company_settings.get('company_address', 'Franchise Head Office, India')}<br/>
            <b>Phone:</b> {company_settings.get('company_phone', '+91 1234567890')}<br/>
            <b>Email:</b> {company_settings.get('company_email', 'info@bigbeancafe.in')}<br/>
            <b>GSTIN:</b> {company_settings.get('company_gstin', '22AAAAA0000A1Z5')}
            """
            
            header_data = [[
                Paragraph(company_info_text, company_info_style),
                logo
            ]]
            
            header_table = Table(header_data, colWidths=[5.2*inch, 1.8*inch])
            header_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ]))
            story.append(header_table)
        except Exception as e:
            print(f"Logo error: {e}")
            # Fallback without logo
            company_text = f"""
            <b><font size=24 color=#3E2723>{company_settings.get('company_name', 'BigBeanCafe')}</font></b><br/>
            {company_settings.get('company_address', 'Franchise Head Office, India')}<br/>
            <b>Phone:</b> {company_settings.get('company_phone', '+91 1234567890')}<br/>
            <b>Email:</b> {company_settings.get('company_email', 'info@bigbeancafe.in')}<br/>
            <b>GSTIN:</b> {company_settings.get('company_gstin', '22AAAAA0000A1Z5')}
            """
            story.append(Paragraph(company_text, company_info_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Divider line
    line_table = Table([['']], colWidths=[7*inch])
    line_table.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,0), 2, COFFEE_DARK),
    ]))
    story.append(line_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Tax Invoice header
    invoice_title = Paragraph('<font size=20 color=#6F4E37><b>TAX INVOICE</b></font>', styles['Normal'])
    invoice_title_table = Table([[invoice_title]], colWidths=[7*inch])
    invoice_title_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CREAM),
        ('PADDING', (0,0), (-1,-1), 12),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    story.append(invoice_title_table)
    story.append(Spacer(1, 0.15*inch))
    
    # Invoice and billing details
    invoice_date_formatted = invoice_data['invoice_date'].strftime('%d-%B-%Y')
    
    details_data = [
        [
            Paragraph('<b>Invoice Details:</b>', heading_style),
            Paragraph('<b>Bill To:</b>', heading_style)
        ],
        [
            Paragraph(f"<b>Invoice No:</b><br/>{invoice_data['invoice_number']}", info_value_style),
            Paragraph(f"<b>{invoice_data['franchise_name']}</b><br/>{invoice_data.get('franchise_address', '')}", info_value_style)
        ],
        [
            Paragraph(f"<b>Invoice Date:</b><br/>{invoice_date_formatted}", info_value_style),
            Paragraph(f"<b>GSTIN:</b> {invoice_data.get('franchise_gstin', 'N/A')}", info_value_style)
        ],
        [
            Paragraph(f"<b>Order ID:</b><br/>{invoice_data['order_id'][:25]}...", info_value_style),
            ''
        ]
    ]
    
    details_table = Table(details_data, colWidths=[3.5*inch, 3.5*inch])
    details_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), COFFEE_LIGHT),
        ('BACKGROUND', (1,0), (1,0), COFFEE_LIGHT),
        ('PADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOX', (0,0), (-1,-1), 1.5, COFFEE_DARK),
        ('INNERGRID', (0,1), (-1,-1), 0.5, COFFEE_LIGHT),
    ]))
    story.append(details_table)
    story.append(Spacer(1, 0.25*inch))
    
    # Order details heading
    story.append(Paragraph('<b>Order Details:</b>', heading_style))
    story.append(Spacer(1, 0.08*inch))
    
    # Items table with SGST/CGST
    table_data = [
        [
            Paragraph('<b>#</b>', info_value_style),
            Paragraph('<b>Product</b>', info_value_style),
            Paragraph('<b>Qty</b>', info_value_style),
            Paragraph('<b>Rate<br/>(₹)</b>', info_value_style),
            Paragraph('<b>Taxable<br/>(₹)</b>', info_value_style),
            Paragraph('<b>SGST<br/>%</b>', info_value_style),
            Paragraph('<b>SGST<br/>(₹)</b>', info_value_style),
            Paragraph('<b>CGST<br/>%</b>', info_value_style),
            Paragraph('<b>CGST<br/>(₹)</b>', info_value_style),
            Paragraph('<b>Total<br/>(₹)</b>', info_value_style)
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
            Paragraph(f"{sgst_percent:.1f}", info_value_style),
            Paragraph(f"{sgst_amount:.2f}", info_value_style),
            Paragraph(f"{cgst_percent:.1f}", info_value_style),
            Paragraph(f"{cgst_amount:.2f}", info_value_style),
            Paragraph(f"<b>{item['total_amount']:.2f}</b>", info_value_style)
        ])
    
    col_widths = [0.3*inch, 2.1*inch, 0.4*inch, 0.6*inch, 0.75*inch, 0.45*inch, 0.6*inch, 0.45*inch, 0.6*inch, 0.75*inch]
    
    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HEADER_BG),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('PADDING', (0, 0), (-1, 0), 8),
        
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),
        ('ALIGN', (2, 1), (-1, -1), 'CENTER'),
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('PADDING', (0, 1), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, CREAM]),
        
        ('GRID', (0, 0), (-1, -1), 0.5, COFFEE_MEDIUM),
        ('BOX', (0, 0), (-1, -1), 1.5, COFFEE_DARK),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 0.2*inch))
    
    # Totals
    sgst_total = invoice_data.get('sgst_total', invoice_data['gst_total'] / 2)
    cgst_total = invoice_data.get('cgst_total', invoice_data['gst_total'] / 2)
    
    totals_data = [
        ['', '', 'Subtotal:', f"₹ {invoice_data['subtotal']:,.2f}"],
        ['', '', 'SGST Total:', f"₹ {sgst_total:,.2f}"],
        ['', '', 'CGST Total:', f"₹ {cgst_total:,.2f}"],
        ['', '', 'Total Tax:', f"₹ {invoice_data['gst_total']:,.2f}"],
    ]
    
    totals_table = Table(totals_data, colWidths=[2.5*inch, 2.5*inch, 1.2*inch, 0.8*inch])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
        ('FONTNAME', (2, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (2, 0), (-1, -1), 9),
        ('PADDING', (2, 0), (-1, -1), 5),
        ('LINEABOVE', (2, -1), (-1, -1), 1, COFFEE_LIGHT),
    ]))
    story.append(totals_table)
    
    # Grand Total
    grand_total_data = [['', '', 'GRAND TOTAL:', f"₹ {invoice_data['grand_total']:,.2f}"]]
    grand_total_table = Table(grand_total_data, colWidths=[2.5*inch, 2.5*inch, 1.2*inch, 0.8*inch])
    grand_total_table.setStyle(TableStyle([
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (2, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (2, 0), (-1, -1), 12),
        ('TEXTCOLOR', (2, 0), (-1, -1), COFFEE_DARK),
        ('BACKGROUND', (2, 0), (-1, -1), CREAM),
        ('PADDING', (2, 0), (-1, -1), 10),
        ('BOX', (2, 0), (-1, -1), 2, COFFEE_DARK),
    ]))
    story.append(grand_total_table)
    story.append(Spacer(1, 0.15*inch))
    
    # Amount in words
    amount_words = number_to_words(invoice_data['grand_total'])
    story.append(Paragraph(f'<b>Amount in Words:</b> <i>{amount_words}</i>', info_value_style))
    story.append(Spacer(1, 0.25*inch))
    
    # Terms
    terms_style = ParagraphStyle('Terms', parent=styles['Normal'], fontSize=7.5, textColor=colors.grey, leading=10)
    story.append(Paragraph('<b>Terms & Conditions:</b>', heading_style))
    terms = """
    1. This is a computer-generated invoice and does not require a physical signature. 
    2. Credit deducted upon order approval. Payment due when credit exhausted (₹1,00,000 fixed). 
    3. All disputes subject to company jurisdiction. Goods once sold not returnable.
    """
    story.append(Paragraph(terms, terms_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Footer
    footer_line = Table([['']], colWidths=[7*inch])
    footer_line.setStyle(TableStyle([('LINEABOVE', (0,0), (-1,0), 1, COFFEE_LIGHT)]))
    story.append(footer_line)
    story.append(Spacer(1, 0.08*inch))
    
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=COFFEE_MEDIUM, alignment=TA_CENTER)
    footer_text = f"""
    <b>Thank you for your business!</b><br/>
    BigBeanCafe Franchise System | {company_settings.get('company_email', 'info@bigbeancafe.in')} | 
    {company_settings.get('company_phone', '+91 1234567890')}
    """
    story.append(Paragraph(footer_text, footer_style))
    
    doc.build(story)
    return str(filepath)

def number_to_words(num):
    """Convert number to words"""
    try:
        num = float(num)
        rupees = int(num)
        paise = int(round((num - rupees) * 100))
        
        def convert(n):
            if n == 0: return "Zero"
            ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"]
            tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
            teens = ["Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
            
            if n < 10: return ones[n]
            elif n < 20: return teens[n - 10]
            elif n < 100: return tens[n // 10] + (" " + ones[n % 10] if n % 10 != 0 else "")
            elif n < 1000: return ones[n // 100] + " Hundred" + (" and " + convert(n % 100) if n % 100 != 0 else "")
            elif n < 100000: return convert(n // 1000) + " Thousand" + (" " + convert(n % 1000) if n % 1000 != 0 else "")
            elif n < 10000000: return convert(n // 100000) + " Lakh" + (" " + convert(n % 100000) if n % 100000 != 0 else "")
            else: return convert(n // 10000000) + " Crore" + (" " + convert(n % 10000000) if n % 10000000 != 0 else "")
        
        result = "Rupees " + convert(rupees)
        if paise > 0:
            result += " and " + convert(paise) + " Paise"
        result += " Only"
        return result
    except:
        return "Amount conversion error"

def get_next_invoice_number(year: int) -> str:
    return f"{year}-{datetime.now().strftime('%m%d%H%M%S')}"
