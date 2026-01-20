from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from flask import send_file
from config.db_config import get_db_connection
import os
import datetime


def generate_invoice_pdf(bill_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch bill & customer
    cursor.execute("""
        SELECT bills.*, customers.customer_name, customers.phone,
               customers.address, customers.gstin
        FROM bills
        LEFT JOIN customers ON bills.customer_id = customers.id
        WHERE bills.id = %s
    """, (bill_id,))
    bill = cursor.fetchone()

    # Fetch items
    cursor.execute("""
        SELECT products.product_name, bill_items.quantity, bill_items.price
        FROM bill_items
        JOIN products ON bill_items.product_id = products.id
        WHERE bill_items.bill_id = %s
    """, (bill_id,))
    items = cursor.fetchall()
    conn.close()

    # File path
    file_path = f"static/invoices/invoice_{bill_id}.pdf"
    os.makedirs("static/invoices", exist_ok=True)

    doc = SimpleDocTemplate(file_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    title_style = ParagraphStyle(
        name="TitleStyle",
        fontSize=18,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )

    elements.append(Paragraph("Retail Billing Invoice", title_style))
    elements.append(Spacer(1, 12))

    details = f"""
    <b>Bill ID:</b> {bill['id']}<br/>
    <b>Date:</b> {bill['created_at']}<br/>
    """

    if bill["customer_name"]:
        details += f"""
        <b>Customer:</b> {bill['customer_name']}<br/>
        <b>Phone:</b> {bill['phone']}<br/>
        <b>GSTIN:</b> {bill['gstin']}<br/>
        <b>Address:</b> {bill['address']}<br/>
        """
    else:
        details += "<b>Customer:</b> Walk-in Customer<br/>"

    elements.append(Paragraph(details, styles["Normal"]))
    elements.append(Spacer(1, 12))

    table_data = [["Product", "Qty", "Price", "Total"]]
    for i in items:
        table_data.append([
            i["product_name"],
            i["quantity"],
            f"₹ {i['price']}",
            f"₹ {i['quantity'] * i['price']}"
        ])

    table = Table(table_data, colWidths=[200, 80, 80, 80])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(
        f"<b>Total Amount: ₹ {bill['total_amount']}</b>",
        styles["Heading2"]
    ))

    doc.build(elements)

    return send_file(file_path, as_attachment=True)
