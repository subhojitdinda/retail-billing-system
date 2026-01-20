from flask import render_template, request, redirect
from config.db_config import get_db_connection


def manage_products():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Add or Update Product
    if request.method == "POST":
        product_id = request.form.get("product_id")
        product_name = request.form["product_name"]
        price = request.form["price"]
        stock = request.form["stock"]
        gst_id = request.form["gst_id"]

        # 🔥 Fetch GST Percentage from gst table
        cursor.execute("SELECT gst_percent FROM gst WHERE id=%s", (gst_id,))
        gst_row = cursor.fetchone()
        gst_percent = gst_row["gst_percent"] if gst_row else 0

        if product_id:  # UPDATE
            cursor.execute("""
                UPDATE products 
                SET product_name=%s,
                    price=%s,
                    stock=%s,
                    gst_id=%s,
                    gst_percent=%s
                WHERE id=%s
            """, (product_name, price, stock, gst_id, gst_percent, product_id))
        else:  # INSERT
            cursor.execute("""
                INSERT INTO products (product_name, price, stock, gst_id, gst_percent)
                VALUES (%s, %s, %s, %s, %s)
            """, (product_name, price, stock, gst_id, gst_percent))

        conn.commit()
        return redirect("/admin/products")

    # Fetch GST slabs for dropdown
    cursor.execute("SELECT * FROM gst")
    gst_list = cursor.fetchall()

    # Fetch products with GST %
    cursor.execute("""
        SELECT products.*, gst.gst_percent AS gst_master_percent
        FROM products 
        LEFT JOIN gst ON products.gst_id = gst.id
        ORDER BY products.id DESC
    """)
    products = cursor.fetchall()

    conn.close()
    return render_template("admin/products.html", products=products, gst_list=gst_list)


def delete_product(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM products WHERE id=%s", (product_id,))
    conn.commit()
    conn.close()

    return redirect("/admin/products")
