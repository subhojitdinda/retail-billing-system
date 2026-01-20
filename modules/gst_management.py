from flask import render_template, request, redirect
from config.db_config import get_db_connection

def manage_gst():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Add new GST
    if request.method == "POST":
        gst_name = request.form['gst_name']
        gst_percent = request.form['gst_percent']

        cursor.execute(
            "INSERT INTO gst (gst_name, gst_percent) VALUES (%s, %s)",
            (gst_name, gst_percent)
        )
        conn.commit()

    # Fetch GST list
    cursor.execute("SELECT * FROM gst")
    gst_list = cursor.fetchall()
    conn.close()

    return render_template("admin/gst.html", gst_list=gst_list)


def delete_gst(gst_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM gst WHERE id = %s", (gst_id,))
    conn.commit()
    conn.close()
    return redirect("/admin/gst")
