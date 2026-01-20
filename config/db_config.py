import mysql.connector

def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",        # your phpMyAdmin username
        password="",        # your phpMyAdmin password (blank if none)
        database="retail_billing_system"
    )
    return connection
