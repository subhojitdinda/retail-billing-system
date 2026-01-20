from flask import render_template, request, redirect, session
from config.db_config import get_db_connection
from utils.security import verify_password

def login_user():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT users.*, roles.role_name 
        FROM users 
        JOIN roles ON users.role_id = roles.id
        WHERE username = %s AND is_active = 1
        """
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        conn.close()

        if user and verify_password(password, user['password']):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role_name']

            # Role based redirect
            if user['role_name'] == 'Admin':
                return redirect("/dashboard/admin")
            elif user['role_name'] == 'Cashier':
                return redirect("/dashboard/cashier")
            elif user['role_name'] == 'Inventory Manager':
                return redirect("/dashboard/inventory")
            else:
                return "Role not defined"

        else:
            return render_template("auth/login.html", error="Invalid Username or Password")

    return render_template("auth/login.html")
