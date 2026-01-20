from flask import render_template, request
from config.db_config import get_db_connection

def sales_report():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Daily sales
    cursor.execute("""
        SELECT DATE(created_at) as sale_date, SUM(total_amount) as total
        FROM bills
        GROUP BY DATE(created_at)
        ORDER BY sale_date DESC
    """)
    daily_sales = cursor.fetchall()

    # Monthly sales
    cursor.execute("""
        SELECT DATE_FORMAT(created_at, '%Y-%m') as sale_month,
               SUM(total_amount) as total
        FROM bills
        GROUP BY sale_month
        ORDER BY sale_month DESC
    """)
    monthly_sales = cursor.fetchall()

    # Product wise sales
    cursor.execute("""
        SELECT products.product_name,
               SUM(bill_items.quantity) as total_qty,
               SUM(bill_items.quantity * bill_items.price) as total_amount
        FROM bill_items
        JOIN products ON bill_items.product_id = products.id
        GROUP BY products.product_name
        ORDER BY total_qty DESC
    """)
    product_sales = cursor.fetchall()

    conn.close()
    return render_template(
        "reports/sales_report.html",
        daily_sales=daily_sales,
        monthly_sales=monthly_sales,
        product_sales=product_sales
    )
