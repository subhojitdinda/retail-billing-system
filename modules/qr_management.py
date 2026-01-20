import qrcode
import os
from flask import render_template, redirect, send_file
from config.db_config import get_db_connection

# Folder where QR images will be saved
QR_FOLDER = "static/qr"

# Ensure QR folder exists
if not os.path.exists(QR_FOLDER):
    os.makedirs(QR_FOLDER)


# ================= QR LIST PAGE =================
def qr_page():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, product_name, qr_code
        FROM products
        ORDER BY id DESC
    """)
    products = cursor.fetchall()
    conn.close()

    return render_template("inventory/qr_generator.html", products=products)


# ================= GENERATE QR =================
def generate_qr(product_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    product = cursor.fetchone()

    if product:
        # QR contains only product ID
        qr_data = str(product_id)

        # File name
        qr_filename = f"product_{product_id}.png"
        qr_path = os.path.join(QR_FOLDER, qr_filename)

        # Generate QR
        img = qrcode.make(qr_data)
        img.save(qr_path)

        # Save filename in DB
        cursor.execute(
            "UPDATE products SET qr_code = %s WHERE id = %s",
            (qr_filename, product_id)
        )
        conn.commit()

    conn.close()
    return redirect("/inventory/qr")


# ================= PRINT QR =================
def print_qr(product_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT qr_code FROM products WHERE id = %s",
        (product_id,)
    )
    product = cursor.fetchone()
    conn.close()

    if not product or not product["qr_code"]:
        return redirect("/inventory/qr")

    qr_path = os.path.join(QR_FOLDER, product["qr_code"])
    return send_file(qr_path, mimetype="image/png")
