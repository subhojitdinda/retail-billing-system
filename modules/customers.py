from flask import render_template, request, redirect, jsonify, session
from config.db_config import get_db_connection


# ================= ADMIN CUSTOMER MANAGEMENT =================
def manage_customers():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        customer_name = request.form["customer_name"]
        phone = request.form["phone"]
        email = request.form.get("email")
        address = request.form.get("address")
        gstin = request.form.get("gstin")

        cursor.execute("""
            INSERT INTO customers (customer_name, phone, email, address, gstin)
            VALUES (%s, %s, %s, %s, %s)
        """, (customer_name, phone, email, address, gstin))
        conn.commit()

    cursor.execute("SELECT * FROM customers ORDER BY id DESC")
    customers = cursor.fetchall()
    conn.close()

    return render_template("customers/manage_customers.html", customers=customers)


# ================= BILLING : SEARCH CUSTOMER BY PHONE =================
def search_customer_by_phone():
    phone = request.args.get("phone")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM customers WHERE phone = %s
    """, (phone,))
    customer = cursor.fetchone()
    conn.close()

    if customer:
        # Save in session for billing
        session["billing_customer_id"] = customer["id"]
        session["billing_customer_name"] = customer["customer_name"]
        session["billing_customer_phone"] = customer["phone"]

        return jsonify({
            "status": "found",
            "customer": {
                "id": customer["id"],
                "name": customer["customer_name"],
                "phone": customer["phone"]
            }
        })
    else:
        return jsonify({"status": "not_found"})


# ================= BILLING : ADD NEW CUSTOMER =================
def add_customer_from_billing():
    data = request.json

    customer_name = data.get("customer_name")
    phone = data.get("phone")
    email = data.get("email")
    address = data.get("address")
    gstin = data.get("gstin")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        INSERT INTO customers (customer_name, phone, email, address, gstin)
        VALUES (%s, %s, %s, %s, %s)
    """, (customer_name, phone, email, address, gstin))
    conn.commit()

    customer_id = cursor.lastrowid
    conn.close()

    # Store in session immediately
    session["billing_customer_id"] = customer_id
    session["billing_customer_name"] = customer_name
    session["billing_customer_phone"] = phone

    return jsonify({
        "status": "success",
        "customer": {
            "id": customer_id,
            "name": customer_name,
            "phone": phone
        }
    })
