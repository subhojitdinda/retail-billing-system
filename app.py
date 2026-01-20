from flask import Flask, render_template, session, redirect, request
from modules.auth import login_user
from modules.roles import role_required
from config.db_config import get_db_connection

# Admin modules
from modules.roles_management import manage_roles, delete_role
from modules.users_management import manage_users, toggle_user, delete_user
from modules.gst_management import manage_gst, delete_gst
from modules.products_management import manage_products, delete_product

# Customers
from modules.customers import (
    manage_customers,
    search_customer_by_phone,
    add_customer_from_billing
)

# Billing
from modules.billing import (
    billing_page,
    remove_from_cart,
    save_bill,
    invoice_page,
    add_product_by_qr
)

# Bill History
from modules.bill_history import bill_history_page

# PDF Invoice
from modules.pdf_invoice import generate_invoice_pdf

# Reports
from modules.reports import sales_report

# Inventory QR
from modules.qr_management import qr_page, generate_qr, print_qr

# Settings
from modules.settings import get_user_theme, toggle_theme

app = Flask(__name__)
app.secret_key = "retail_billing_secret_key"


# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    return login_user()


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ---------------- TOGGLE THEME ----------------
@app.route("/toggle-theme")
def toggle_theme_route():
    if "user_id" in session:
        toggle_theme(session["user_id"])
    return redirect(request.referrer or "/")


# ---------------- DASHBOARDS ----------------
@app.route("/dashboard/admin")
@role_required("Admin")
def admin_dashboard():
    theme = get_user_theme(session["user_id"])

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT IFNULL(SUM(grand_total),0) AS total_sales FROM bills")
    total_sales = cursor.fetchone()["total_sales"]

    cursor.execute("""
        SELECT IFNULL(SUM(grand_total),0) AS today_sales
        FROM bills WHERE DATE(created_at)=CURDATE()
    """)
    today_sales = cursor.fetchone()["today_sales"]

    cursor.execute("SELECT COUNT(*) AS total_bills FROM bills")
    total_bills = cursor.fetchone()["total_bills"]

    cursor.execute("SELECT COUNT(*) AS total_products FROM products")
    total_products = cursor.fetchone()["total_products"]

    cursor.execute("""
        SELECT DATE_FORMAT(created_at,'%b') AS month, SUM(grand_total) AS total
        FROM bills GROUP BY MONTH(created_at) ORDER BY MONTH(created_at)
    """)
    monthly = cursor.fetchall()
    monthly_labels = [m["month"] for m in monthly]
    monthly_sales = [float(m["total"]) for m in monthly]

    cursor.execute("""
        SELECT p.product_name, SUM(bi.quantity) AS qty
        FROM bill_items bi
        JOIN products p ON bi.product_id = p.id
        GROUP BY bi.product_id
        ORDER BY qty DESC LIMIT 5
    """)
    top_products = cursor.fetchall()
    top_product_labels = [p["product_name"] for p in top_products]
    top_product_values = [int(p["qty"]) for p in top_products]

    conn.close()

    return render_template(
        "dashboard/admin.html",
        theme=theme,
        total_sales=total_sales,
        today_sales=today_sales,
        total_bills=total_bills,
        total_products=total_products,
        monthly_labels=monthly_labels,
        monthly_sales=monthly_sales,
        top_product_labels=top_product_labels,
        top_product_values=top_product_values
    )


@app.route("/dashboard/cashier")
@role_required("Cashier")
def cashier_dashboard():
    theme = get_user_theme(session["user_id"])
    return render_template("dashboard/cashier.html", theme=theme)


@app.route("/dashboard/inventory")
@role_required("Inventory Manager")
def inventory_dashboard():
    theme = get_user_theme(session["user_id"])
    return render_template("dashboard/inventory.html", theme=theme)


# ================= ADMIN MANAGEMENT =================

@app.route("/admin/roles", methods=["GET", "POST"])
@role_required("Admin")
def admin_roles():
    return manage_roles()


@app.route("/admin/roles/delete/<int:role_id>")
@role_required("Admin")
def admin_roles_delete(role_id):
    return delete_role(role_id)


@app.route("/admin/users", methods=["GET", "POST"])
@role_required("Admin")
def admin_users():
    return manage_users()


@app.route("/admin/users/toggle/<int:user_id>")
@role_required("Admin")
def admin_users_toggle(user_id):
    return toggle_user(user_id)


@app.route("/admin/users/delete/<int:user_id>")
@role_required("Admin")
def admin_users_delete(user_id):
    return delete_user(user_id)


@app.route("/admin/gst", methods=["GET", "POST"])
@role_required("Admin")
def admin_gst():
    return manage_gst()


@app.route("/admin/gst/delete/<int:gst_id>")
@role_required("Admin")
def admin_gst_delete(gst_id):
    return delete_gst(gst_id)


@app.route("/admin/products", methods=["GET", "POST"])
@role_required("Admin")
def admin_products():
    return manage_products()


@app.route("/admin/products/delete/<int:product_id>")
@role_required("Admin")
def admin_products_delete(product_id):
    return delete_product(product_id)


# ================= INVENTORY MANAGER PRODUCT POWER =================
# Same product management, different URL and same functions

@app.route("/inventory/products", methods=["GET", "POST"])
@role_required("Inventory Manager")
def inventory_products():
    return manage_products()


@app.route("/inventory/products/delete/<int:product_id>")
@role_required("Inventory Manager")
def inventory_products_delete(product_id):
    return delete_product(product_id)


# ================= CUSTOMER MANAGEMENT =================

@app.route("/customers", methods=["GET", "POST"])
@role_required("Admin")
def customers():
    return manage_customers()


# ================= BILLING =================

@app.route("/billing", methods=["GET", "POST"])
@role_required("Cashier")
def billing():
    return billing_page()


@app.route("/billing/remove/<int:product_id>")
@role_required("Cashier")
def billing_remove(product_id):
    return remove_from_cart(product_id)


@app.route("/billing/qr-add/<int:product_id>")
@role_required("Cashier")
def billing_qr_add(product_id):
    return add_product_by_qr(product_id)


@app.route("/billing/save")
@role_required("Cashier")
def billing_save():
    return save_bill(session["user_id"])


@app.route("/invoice/<int:bill_id>")
@role_required("Cashier")
def invoice(bill_id):
    return invoice_page(bill_id)


@app.route("/invoice/pdf/<int:bill_id>")
@role_required("Cashier")
def invoice_pdf(bill_id):
    return generate_invoice_pdf(bill_id)


# ================= BILL HISTORY =================

@app.route("/billing/history")
@role_required("Cashier")
def billing_history():
    return bill_history_page()


# ================= REPORTS =================

@app.route("/reports/sales")
@role_required("Admin")
def reports_sales():
    return sales_report()


# ================= INVENTORY QR =================

@app.route("/inventory/qr")
@role_required("Admin", "Inventory Manager")
def inventory_qr():
    return qr_page()


@app.route("/inventory/qr/generate/<int:product_id>")
@role_required("Admin", "Inventory Manager")
def inventory_generate_qr(product_id):
    return generate_qr(product_id)


@app.route("/inventory/qr/print/<int:product_id>")
@role_required("Admin", "Inventory Manager")
def inventory_print_qr(product_id):
    return print_qr(product_id)


# ================= BILLING CUSTOMER ROUTES =================

@app.route("/billing/search-customer")
@role_required("Cashier")
def billing_search_customer():
    return search_customer_by_phone()


@app.route("/billing/add-customer", methods=["POST"])
@role_required("Cashier")
def billing_add_customer():
    return add_customer_from_billing()


@app.route("/billing/reset-customer")
@role_required("Cashier")
def reset_billing_customer():
    session.pop("billing_customer_id", None)
    session.pop("billing_customer_name", None)
    session.pop("billing_customer_phone", None)
    session["cart"] = []
    session.modified = True
    return redirect("/billing")


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
