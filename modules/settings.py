from config.db_config import get_db_connection

def get_user_theme(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT theme FROM settings WHERE user_id = %s", (user_id,))
    data = cursor.fetchone()

    # If user has no setting yet, insert default light mode
    if not data:
        cursor.execute(
            "INSERT INTO settings (user_id, theme) VALUES (%s, %s)",
            (user_id, "light")
        )
        conn.commit()
        theme = "light"
    else:
        theme = data["theme"]

    conn.close()
    return theme


def toggle_theme(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT theme FROM settings WHERE user_id = %s", (user_id,))
    data = cursor.fetchone()

    if data["theme"] == "light":
        new_theme = "dark"
    else:
        new_theme = "light"

    cursor.execute(
        "UPDATE settings SET theme = %s WHERE user_id = %s",
        (new_theme, user_id)
    )
    conn.commit()
    conn.close()
