from flask import render_template, request, redirect
from config.db_config import get_db_connection
from utils.security import hash_password

def manage_users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        role_id = request.form['role_id']

        hashed = hash_password(password)

        cursor.execute(
            "INSERT INTO users (username, password, role_id) VALUES (%s, %s, %s)",
            (username, hashed, role_id)
        )
        conn.commit()

    cursor.execute("""
        SELECT users.id, users.username, users.is_active,
               roles.role_name
        FROM users
        JOIN roles ON users.role_id = roles.id
    """)
    users = cursor.fetchall()

    cursor.execute("SELECT * FROM roles")
    roles = cursor.fetchall()

    conn.close()
    return render_template("admin/users.html", users=users, roles=roles)


def toggle_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT is_active FROM users WHERE id = %s", (user_id,))
    status = cursor.fetchone()[0]

    new_status = 0 if status == 1 else 1

    cursor.execute(
        "UPDATE users SET is_active = %s WHERE id = %s",
        (new_status, user_id)
    )
    conn.commit()
    conn.close()
    return redirect("/admin/users")


def delete_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    conn.commit()
    conn.close()
    return redirect("/admin/users")
