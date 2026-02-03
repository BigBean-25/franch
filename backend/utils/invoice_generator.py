from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib import colors
from datetime import datetime
import os
from pathlib import Path

INVOICE_DIR = Path("/app/backend/invoices")
INVOICE_DIR.mkdir(exist_ok=True)

def generate_invoice_pdf(invoice_data: dict, company_settings: dict) -> str:
    """
    Generate invoice PDF and return the file path
    
    invoice_data should contain:
    - invoice_number
    - order_id
    - franchise_name
    - franchise_address
    - franchise_gstin
    - items: [{product_name, quantity, unit_price, gst_percent, taxable_amount, gst_amount, total_amount}]
    - subtotal
    - gst_total
    - grand_total
    - invoice_date
    """
    
    filename = f"BBC-INV-{invoice_data['invoice_number']}.pdf"
    filepath = INVOICE_DIR / filename
    
    doc = SimpleDocTemplate(str(filepath), pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2C3E50'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#34495E'),
        spaceAfter=12
    )
    
    # Company Header
    story.append(Paragraph(company_settings.get('company_name', 'BigBeanCafe'), title_style))
    story.append(Paragraph(f"<b>GSTIN:</b> {company_settings.get('company_gstin', '')} | <b>Phone:</b> {company_settings.get('company_phone', '')}", styles['Normal']))
    story.append(Paragraph(company_settings.get('company_address', ''), styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Invoice Info
    story.append(Paragraph(f"<b>TAX INVOICE</b>", heading_style))
    story.append(Paragraph(f"<b>Invoice No:</b> {invoice_data['invoice_number']}", styles['Normal']))
    story.append(Paragraph(f"<b>Date:</b> {invoice_data['invoice_date'].strftime('%d-%b-%Y')}", styles['Normal']))
    story.append(Paragraph(f"<b>Order ID:</b> {invoice_data['order_id']}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Franchise Details
    story.append(Paragraph(f"<b>Bill To:</b>", heading_style))
    story.append(Paragraph(f"<b>{invoice_data['franchise_name']}</b>", styles['Normal']))
    if invoice_data.get('franchise_address'):
        story.append(Paragraph(invoice_data['franchise_address'], styles['Normal']))
    if invoice_data.get('franchise_gstin'):
        story.append(Paragraph(f"<b>GSTIN:</b> {invoice_data['franchise_gstin']}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Items Table
    table_data = [
        ['#', 'Product', 'Qty', 'Rate', 'Taxable', 'SGST%', 'SGST', 'CGST%', 'CGST', 'Total']
    ]
    
    for idx, item in enumerate(invoice_data['items'], 1):
        table_data.append([
            str(idx),
            item['product_name'],
            str(item['quantity']),
            f"₹{item['unit_price']:.2f}",
            f"₹{item['taxable_amount']:.2f}",
            f"{item.get('sgst_percent', item['gst_percent']/2):.1f}%",
            f"₹{item.get('sgst_amount', item['gst_amount']/2):.2f}",
            f"{item.get('cgst_percent', item['gst_percent']/2):.1f}%",
            f"₹{item.get('cgst_amount', item['gst_amount']/2):.2f}",
            f"₹{item['total_amount']:.2f}"
        ])
    
    # Add totals
    table_data.append(['', '', '', '', '<b>Subtotal</b>', '', '', '', '', f"<b>₹{invoice_data['subtotal']:.2f}</b>"])
    table_data.append(['', '', '', '', '<b>SGST Total</b>', '', '', '', '', f"<b>₹{invoice_data.get('sgst_total', invoice_data['gst_total']/2):.2f}</b>"])
    table_data.append(['', '', '', '', '<b>CGST Total</b>', '', '', '', '', f"<b>₹{invoice_data.get('cgst_total', invoice_data['gst_total']/2):.2f}</b>"])
    table_data.append(['', '', '', '', '<b>Grand Total</b>', '', '', '', '', f"<b>₹{invoice_data['grand_total']:.2f}</b>"])
    
    # Create table
    table = Table(table_data, colWidths=[0.3*inch, 1.5*inch, 0.4*inch, 0.7*inch, 0.9*inch, 0.5*inch, 0.7*inch, 0.5*inch, 0.7*inch, 0.9*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -4), colors.beige),
        ('GRID', (0, 0), (-1, -5), 1, colors.black),
        ('BACKGROUND', (0, -4), (-1, -1), colors.HexColor('#ECF0F1')),
        ('FONTNAME', (0, -4), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -4), (-1, -1), 11),
        ('SPAN', (0, -4), (8, -4)),
        ('SPAN', (0, -3), (8, -3)),
        ('SPAN', (0, -2), (8, -2)),
        ('SPAN', (0, -1), (8, -1)),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 0.5*inch))
    
    # Footer
    story.append(Paragraph("<b>Terms & Conditions:</b>", styles['Normal']))
    story.append(Paragraph("1. Credit will be deducted upon order approval.", styles['Normal']))
    story.append(Paragraph("2. Payment due when credit limit is exhausted.", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("<i>This is a computer-generated invoice and does not require a signature.</i>", styles['Normal']))
    
    # Build PDF
    doc.build(story)
    
    return str(filepath)

def get_next_invoice_number(year: int) -> str:
    """
    Generate next invoice number in format: YYYY-0001
    """
    # This would normally query the database for the last invoice number
    # For now, we'll use a simple format
    return f"{year}-{datetime.now().strftime('%m%d%H%M%S')}"
