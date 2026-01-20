# 🧾 Retail Billing System with QR Code Support

A complete Retail Billing System built using **Flask (Python)** and **MySQL**, designed for small and medium shops.  
It supports role-based access, product management, customer handling, billing, invoice generation, and QR code scanning for fast billing.

---

## 🚀 Features

- 🔐 Role Based Login  
  - Admin  
  - Cashier  
  - Inventory Manager  

- 📦 Product Management  
  - Add / Edit / Delete products  
  - GST assignment  
  - Stock management  

- 🧾 Billing System  
  - Manual product add  
  - QR code scan to select product  
  - Auto focus on quantity after scan  
  - Customer lock system  
  - Cart management  
  - GST & total calculation  
  - Invoice generation (PDF supported)

- 📷 QR Code System  
  - QR generation for each product  
  - QR scanning using camera  
  - Beep sound on successful scan  
  - Camera auto-close after scan  
  - Loader while opening camera  

- 👥 Customer Management  
  - Search customer by phone  
  - Add new customer  
  - Auto assign during billing  

- 📊 Reports  
  - Sales report  
  - Bill history  

- 🎨 Theme Support  
  - Light / Dark mode per user  

---

## 📁 Project Folder Structure




retail_billing_system/
│
├── app.py # Main Flask application
├── config/
│ └── db_config.py # MySQL database connection
│
├── modules/
│ ├── auth.py # Login authentication
│ ├── roles.py # Role based access control
│ ├── billing.py # Billing & QR product add
│ ├── customers.py # Customer management
│ ├── products_management.py
│ ├── gst_management.py
│ ├── qr_management.py # QR generation & print
│ ├── reports.py
│ ├── pdf_invoice.py
│ ├── bill_history.py
│ ├── settings.py
│
├── templates/
│ ├── base.html
│ ├── billing/
│ │ ├── billing.html
│ │ └── invoice.html
│ ├── inventory/
│ │ └── qr_generator.html
│ ├── dashboard/
│ │ ├── admin.html
│ │ ├── cashier.html
│ │ └── inventory.html
│
├── static/
│ ├── qr/ # Generated QR images
│ ├── js/
│ │ └── html5-qrcode.min.js
│ └── css/
│
├── .gitignore # Ignored files & folders
├── README.md # Project documentation





---

## 💻 Technologies Used

- Python (Flask)
- MySQL
- HTML / CSS / JavaScript
- QR Code Library (local html5-qrcode)
- Bootstrap (optional styling)

---

## 🧠 How QR Scan Works

1. Click 📷 Scan QR  
2. Loader appears  
3. Camera opens  
4. QR scanned  
5. Beep sound plays  
6. Product auto-selected  
7. Quantity box focused  
8. Camera auto-closes  
9. Click **Add Product**

---

## 📌 Developed By

**Subhojit Dinda**  
Retail Billing System – 2026  
Built with practical business usage in mind.

---

## 🔄 Git Upload Workflow

```bash
git status
git add .
git commit -m "Your update message"
git push
