from flask import render_template, request, redirect
from config.db_config import get_db_connection

def manage_roles():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        role_name = request.form['role_name']
        description = request.form['description']

        cursor.execute(
            "INSERT INTO roles (role_name, description) VALUES (%s, %s)",
            (role_name, description)
        )
        conn.commit()

    cursor.execute("SELECT * FROM roles")
    roles = cursor.fetchall()
    conn.close()

    return render_template("admin/roles.html", roles=roles)


def delete_role(role_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT role_name FROM roles WHERE id = %s", (role_id,))
    role = cursor.fetchone()

    if role and role[0] != "Admin":
        cursor.execute("DELETE FROM roles WHERE id = %s", (role_id,))
        conn.commit()

    conn.close()
    return redirect("/admin/roles")
