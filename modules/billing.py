from flask import render_template, request, session, redirect, jsonify
from config.db_config import get_db_connection


# ================= BILLING PAGE =================
def billing_page():
    if "cart" not in session:
        session["cart"] = []

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch products with GST percent
    cursor.execute("""
        SELECT p.*, g.gst_percent
        FROM products p
        LEFT JOIN gst g ON p.gst_id = g.id
    """)
    products = cursor.fetchall()

    billing_customer = None
    if "billing_customer_id" in session:
        billing_customer = {
            "id": session["billing_customer_id"],
            "name": session["billing_customer_name"],
            "phone": session["billing_customer_phone"]
        }

    # Add product manually
    if request.method == "POST":
        product_id = int(request.form["product_id"])
        quantity = int(request.form["quantity"])

        cursor.execute("""
            SELECT p.*, g.gst_percent
            FROM products p
            LEFT JOIN gst g ON p.gst_id = g.id
            WHERE p.id = %s
        """, (product_id,))
        product = cursor.fetchone()

        if not product or quantity > product["stock"]:
            conn.close()
            return redirect("/billing")

        add_product_to_cart(product, quantity)
        session.modified = True

    subtotal = sum(float(i["total"]) for i in session["cart"])
    conn.close()

    return render_template(
        "billing/billing.html",
        products=products,
        cart=session["cart"],
        subtotal=subtotal,
        billing_customer=billing_customer
    )


# ================= COMMON ADD TO CART FUNCTION =================
def add_product_to_cart(product, quantity):
    found = False
    for item in session["cart"]:
        if item["product_id"] == product["id"]:
            item["quantity"] += quantity
            item["total"] = float(item["quantity"]) * float(item["price"])
            found = True
            break

    if not found:
        session["cart"].append({
            "product_id": product["id"],
            "product_name": product["product_name"],
            "price": float(product["price"]),
            "gst_percent": float(product["gst_percent"]),
            "quantity": quantity,
            "total": float(product["price"]) * quantity
        })


# ================= ADD PRODUCT BY QR (CORE LOGIC) =================
# URL: /billing/qr-add/<product_id>?qty=2
def add_by_qr(product_id):
    qty = request.args.get("qty", 1, type=int)

    if qty <= 0:
        return jsonify({"status": "error", "msg": "Invalid quantity"})

    if "cart" not in session:
        session["cart"] = []

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT p.*, g.gst_percent
        FROM products p
        LEFT JOIN gst g ON p.gst_id = g.id
        WHERE p.id = %s
    """, (product_id,))
    product = cursor.fetchone()

    if not product:
        conn.close()
        return jsonify({"status": "error", "msg": "Product not found"})

    if qty > product["stock"]:
        conn.close()
        return jsonify({"status": "error", "msg": "Not enough stock"})

    add_product_to_cart(product, qty)

    session.modified = True
    conn.close()
    return jsonify({"status": "success"})


# ================= WRAPPER REQUIRED BY app.py =================
# This is ONLY to match your import:
# from modules.billing import add_product_by_qr
def add_product_by_qr(product_id):
    return add_by_qr(product_id)


# ================= REMOVE ITEM FROM CART =================
def remove_from_cart(product_id):
    session["cart"] = [i for i in session["cart"] if i["product_id"] != product_id]
    session.modified = True
    return redirect("/billing")


# ================= SAVE BILL =================
def save_bill(user_id):
    if not session.get("cart"):
        return redirect("/billing")

    customer_id = session.get("billing_customer_id")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    subtotal = sum(float(i["total"]) for i in session["cart"])

    total_gst = 0
    for item in session["cart"]:
        total_gst += (item["total"] * item["gst_percent"]) / 100

    grand_total = subtotal + total_gst

    cursor.execute("""
        INSERT INTO bills (customer_id, user_id, total_amount, gst_amount, grand_total)
        VALUES (%s, %s, %s, %s, %s)
    """, (customer_id, user_id, subtotal, total_gst, grand_total))

    bill_id = cursor.lastrowid

    for item in session["cart"]:
        cursor.execute("""
            INSERT INTO bill_items (bill_id, product_id, quantity, price, gst_percent)
            VALUES (%s, %s, %s, %s, %s)
        """, (bill_id, item["product_id"], item["quantity"], item["price"], item["gst_percent"]))

        cursor.execute("""
            UPDATE products SET stock = stock - %s WHERE id = %s
        """, (item["quantity"], item["product_id"]))

    conn.commit()
    conn.close()

    # Clear billing session
    session["cart"] = []
    session.pop("billing_customer_id", None)
    session.pop("billing_customer_name", None)
    session.pop("billing_customer_phone", None)
    session.modified = True

    return redirect(f"/invoice/{bill_id}")


# ================= INVOICE PAGE =================
def invoice_page(bill_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT b.*, c.customer_name, c.phone
        FROM bills b
        LEFT JOIN customers c ON b.customer_id = c.id
        WHERE b.id = %s
    """, (bill_id,))
    bill = cursor.fetchone()

    cursor.execute("""
        SELECT p.product_name, bi.quantity, bi.price, bi.gst_percent
        FROM bill_items bi
        JOIN products p ON bi.product_id = p.id
        WHERE bi.bill_id = %s
    """, (bill_id,))
    items = cursor.fetchall()

    conn.close()
    return render_template("billing/invoice.html", bill=bill, items=items)
