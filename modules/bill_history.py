from flask import render_template
from config.db_config import get_db_connection

def bill_history_page():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            bills.id,
            users.username AS cashier,
            bills.created_at,
            bills.grand_total
        FROM bills
        LEFT JOIN users ON bills.user_id = users.id
        ORDER BY bills.id DESC
    """)

    bills = cursor.fetchall()
    conn.close()

    return render_template("billing/bill_history.html", bills=bills)
