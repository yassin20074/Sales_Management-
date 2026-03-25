from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from datetime import datetime

def print_bulk_invoice(invoice_id, items, grand_total):
    filename = f"Invoice_{invoice_id}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=(350, 600))
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("SMART RETAIL - RECEIPT", styles['Title']))
    elements.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    elements.append(Paragraph(f"Invoice ID: #{invoice_id}", styles['Normal']))
    elements.append(Spacer(1, 10))

    data = [["Item", "Qty", "Price", "Total"]]
    for item in items:
        data.append([item['name'], str(item['qty']), f"${item['price']}", f"${item['total']}"])
    
    data.append(["", "", "TOTAL:", f"${grand_total:.2f}"])

    table = Table(data, colWidths=[100, 40, 60, 70])
    table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-2), 0.5, colors.grey),
        ('BACKGROUND', (0,0), (-1,0), colors.black),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (-2,-1), (-1,-1), 'Helvetica-Bold'),
    ]))
    
    elements.append(table)
    doc.build(elements)
    return filename