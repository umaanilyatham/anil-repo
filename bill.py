
import os
import random
import smtplib
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from email.message import EmailMessage

import requests
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors


# ==================================================
# CONFIGURATION
# ==================================================

SHOP_NAME = "LAKSHMI JYOTHI RETAILS"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INVOICE_DIR = os.path.join(BASE_DIR, "invoices")

os.makedirs(INVOICE_DIR, exist_ok=True)

# Gmail environment variables
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

# WhatsApp Cloud API environment variables
WA_TOKEN = os.getenv("WA_TOKEN", "")
WA_PHONE_NUMBER_ID = os.getenv("WA_PHONE_NUMBER_ID", "")
WA_API_VERSION = os.getenv("WA_API_VERSION", "v25.0")


# ==================================================
# COLORS
# ==================================================

BG = "#F1F5F9"
WHITE = "#FFFFFF"
BLUE = "#1E3A8A"
LIGHT_BLUE = "#DBEAFE"
DARK = "#172554"
GREEN = "#15803D"
RED = "#DC2626"
GRAY = "#64748B"


# ==================================================
# MAIN WINDOW
# ==================================================

root = tk.Tk()

root.title("Lakshmi Jyothi Retails Billing")
root.geometry("1450x850")
root.minsize(1100, 700)
root.configure(bg=BG)


# ==================================================
# STYLE
# ==================================================

style = ttk.Style()
style.theme_use("clam")

style.configure(
    "Treeview",
    background=WHITE,
    foreground=DARK,
    rowheight=32,
    font=("Arial", 10),
    fieldbackground=WHITE
)

style.configure(
    "Treeview.Heading",
    background=BLUE,
    foreground=WHITE,
    font=("Arial", 10, "bold")
)

style.map(
    "Treeview",
    background=[("selected", LIGHT_BLUE)],
    foreground=[("selected", DARK)]
)


# ==================================================
# VARIABLES
# ==================================================

customer_name = tk.StringVar()
customer_phone = tk.StringVar()
customer_email = tk.StringVar()

product_name = tk.StringVar()
product_rate = tk.StringVar()
product_qty = tk.StringVar()

bill_no = tk.StringVar(
    value=str(random.randint(100000, 999999))
)

grand_total = tk.StringVar(value="Rs. 0.00")
status = tk.StringVar(value="Ready")

items = []

current_pdf = None
bill_generated = False
bill_datetime = None


# ==================================================
# HELPERS
# ==================================================

def update_status(text):
    status.set(text)


def calculate_total():
    return sum(item["total"] for item in items)


def validate_customer():

    if not customer_name.get().strip():
        messagebox.showerror("Error", "Enter customer name")
        return False

    if not customer_phone.get().strip():
        messagebox.showerror("Error", "Enter customer phone")
        return False

    if not customer_email.get().strip():
        messagebox.showerror("Error", "Enter customer email")
        return False

    if "@" not in customer_email.get():
        messagebox.showerror("Error", "Enter valid email")
        return False

    return True


def update_total():
    grand_total.set(
        f"Rs. {calculate_total():,.2f}"
    )


# ==================================================
# ADD PRODUCT
# ==================================================

def add_item():

    global bill_generated, current_pdf

    name = product_name.get().strip()

    if not name:
        messagebox.showerror("Error", "Enter product name")
        return

    try:
        rate = float(product_rate.get())
        qty = int(product_qty.get())

        if rate <= 0 or qty <= 0:
            raise ValueError

    except ValueError:
        messagebox.showerror(
            "Error",
            "Rate and quantity must be positive numbers"
        )
        return

    total = rate * qty

    item = {
        "name": name,
        "rate": rate,
        "qty": qty,
        "total": total
    }

    items.append(item)

    product_table.insert(
        "",
        tk.END,
        values=(
            name,
            qty,
            f"Rs. {rate:.2f}",
            f"Rs. {total:.2f}"
        )
    )

    product_name.set("")
    product_rate.set("")
    product_qty.set("")

    bill_generated = False
    current_pdf = None

    update_total()


# ==================================================
# REMOVE PRODUCT
# ==================================================

def remove_item():

    global bill_generated, current_pdf

    selected = product_table.selection()

    if not selected:
        messagebox.showwarning(
            "Warning", "Select product first"
        )
        return

    for row in selected:
        index = product_table.index(row)
        product_table.delete(row)
        del items[index]

    bill_generated = False
    current_pdf = None

    update_total()


# ==================================================
# GENERATE PDF
# ==================================================

def generate_pdf():

    global current_pdf, bill_generated, bill_datetime

    if not validate_customer():
        return None

    if not items:
        messagebox.showerror(
            "Error", "Add at least one product"
        )
        return None

    bill_datetime = datetime.now()

    filename = f"Invoice_{bill_no.get()}.pdf"

    current_pdf = os.path.join(
        INVOICE_DIR, filename
    )

    c = canvas.Canvas(
        current_pdf,
        pagesize=A4
    )

    width, height = A4

    # Header images
    left_img = os.path.join(BASE_DIR, "vin.jpg")
    right_img = os.path.join(BASE_DIR, "saibaba.jpg")

    if os.path.exists(left_img):
        c.drawImage(
            left_img, 40, height - 105,
            65, 65,
            preserveAspectRatio=True,
            mask="auto"
        )

    if os.path.exists(right_img):
        c.drawImage(
            right_img, width - 105, height - 105,
            65, 65,
            preserveAspectRatio=True,
            mask="auto"
        )

    # Heading
    c.setFillColor(colors.HexColor(BLUE))
    c.setFont("Helvetica-Bold", 20)

    c.drawCentredString(
        width / 2,
        height - 65,
        SHOP_NAME
    )

    c.setFillColor(colors.black)
    c.setFont("Helvetica", 12)

    c.drawCentredString(
        width / 2,
        height - 90,
        "BILLING INVOICE"
    )

    c.line(
        40, height - 120,
        width - 40, height - 120
    )

    y = height - 155

    c.setFont("Helvetica", 10)

    c.drawString(
        50, y, f"Bill No: {bill_no.get()}"
    )

    c.drawString(
        350, y,
        f"Date: {bill_datetime.strftime('%d-%m-%Y')}"
    )

    y -= 22

    c.drawString(
        50, y,
        f"Customer: {customer_name.get()}"
    )

    c.drawString(
        350, y,
        f"Time: {bill_datetime.strftime('%I:%M %p')}"
    )

    y -= 22

    c.drawString(
        50, y,
        f"Phone: {customer_phone.get()}"
    )

    y -= 22

    c.drawString(
        50, y,
        f"Email: {customer_email.get()}"
    )

    y -= 45

    def draw_table_header():

        c.setFillColor(colors.HexColor(LIGHT_BLUE))

        c.rect(
            40, y - 5,
            width - 80, 25,
            fill=1
        )

        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 10)

        c.drawString(50, y + 3, "Product")
        c.drawString(260, y + 3, "Qty")
        c.drawString(350, y + 3, "Rate")
        c.drawString(450, y + 3, "Total")

    draw_table_header()

    y -= 30

    total_amount = 0

    for item in items:

        if y < 90:
            c.showPage()
            y = height - 150
            draw_table_header()
            y -= 30

        c.setFont("Helvetica", 10)

        c.drawString(
            50, y, item["name"][:35]
        )

        c.drawString(
            260, y, str(item["qty"])
        )

        c.drawRightString(
            420, y,
            f"{item['rate']:,.2f}"
        )

        c.drawRightString(
            530, y,
            f"{item['total']:,.2f}"
        )

        total_amount += item["total"]

        y -= 22

    if y < 75:
        c.showPage()
        y = height - 150

    y -= 20

    c.setFont("Helvetica-Bold", 14)

    c.drawString(
        300, y, "Grand Total:"
    )

    c.drawRightString(
        530, y,
        f"Rs. {total_amount:,.2f}"
    )

    y -= 50

    c.setFont("Helvetica-Oblique", 11)

    c.drawCentredString(
        width / 2,
        y,
        "Thank you for shopping with us!"
    )

    c.save()

    bill_generated = True

    return current_pdf


# ==================================================
# PREVIEW BILL
# ==================================================

def generate_bill():

    path = generate_pdf()

    if not path:
        return

    preview.delete("1.0", tk.END)

    preview.insert(
        tk.END,
        f"""
        {SHOP_NAME}
        =============================================

        Bill Number : {bill_no.get()}
        Date        : {bill_datetime.strftime('%d-%m-%Y')}
        Time        : {bill_datetime.strftime('%I:%M %p')}

        Customer    : {customer_name.get()}
        Phone       : {customer_phone.get()}
        Email       : {customer_email.get()}

        =============================================
        PRODUCT        QTY       RATE       TOTAL
        =============================================
"""
    )

    for item in items:

        preview.insert(
            tk.END,
            f"{item['name']:<15} "
            f"{item['qty']:<8} "
            f"{item['rate']:<10.2f} "
            f"{item['total']:.2f}\n"
        )

    preview.insert(
        tk.END,
        "\n=============================================\n"
    )

    preview.insert(
        tk.END,
        f"\nGRAND TOTAL: Rs. {calculate_total():,.2f}"
    )

    preview.insert(
        tk.END,
        "\n\nThank you for shopping with us!"
    )

    update_status("PDF generated successfully")

    messagebox.showinfo(
        "Success",
        f"Invoice generated!\n{path}"
    )


# ==================================================
# EMAIL
# ==================================================

def send_email(pdf_path, recipient, customer, bill, amount):

    if not SMTP_EMAIL or not SMTP_PASSWORD:
        raise ValueError(
            "Gmail credentials are not configured"
        )

    msg = EmailMessage()

    msg["Subject"] = f"Your Invoice - {SHOP_NAME}"
    msg["From"] = SMTP_EMAIL
    msg["To"] = recipient

    msg.set_content(
        f"""
Dear {customer},

Thank you for shopping with {SHOP_NAME}.

Please find your PDF invoice attached.

Bill Number: {bill}
Grand Total: Rs. {amount:,.2f}

Thank you!
{SHOP_NAME}
"""
    )

    with open(pdf_path, "rb") as file:

        msg.add_attachment(
            file.read(),
            maintype="application",
            subtype="pdf",
            filename=os.path.basename(pdf_path)
        )

    with smtplib.SMTP_SSL(
        "smtp.gmail.com", 465, timeout=30
    ) as server:

        server.login(
            SMTP_EMAIL,
            SMTP_PASSWORD
        )

        server.send_message(msg)


# ==================================================
# WHATSAPP CLOUD API
# ==================================================

def send_whatsapp(pdf_path, phone, bill):

    if not WA_TOKEN or not WA_PHONE_NUMBER_ID:
        raise ValueError(
            "WhatsApp API credentials are missing"
        )

    phone = "".join(
        ch for ch in phone if ch.isdigit()
    )

    if not 10 <= len(phone) <= 15:
        raise ValueError(
            "Enter phone with country code, e.g. 919876543210"
        )

    base_url = (
        f"https://graph.facebook.com/"
        f"{WA_API_VERSION}/{WA_PHONE_NUMBER_ID}"
    )

    headers = {
        "Authorization": f"Bearer {WA_TOKEN}"
    }

    # Upload PDF

    with open(pdf_path, "rb") as file:

        response = requests.post(
            f"{base_url}/media",
            headers=headers,
            data={
                "messaging_product": "whatsapp",
                "type": "application/pdf"
            },
            files={
                "file": (
                    os.path.basename(pdf_path),
                    file,
                    "application/pdf"
                )
            },
            timeout=60
        )

    response.raise_for_status()

    media_id = response.json()["id"]

    # Send document

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone,
        "type": "document",
        "document": {
            "id": media_id,
            "filename": os.path.basename(pdf_path),
            "caption": (
                f"Thank you for shopping with {SHOP_NAME}. "
                f"Invoice number: {bill}"
            )
        }
    }

    response = requests.post(
        f"{base_url}/messages",
        headers={
            **headers,
            "Content-Type": "application/json"
        },
        json=payload,
        timeout=60
    )

    response.raise_for_status()

    return response.json()


# ==================================================
# BACKGROUND DELIVERY
# ==================================================

def deliver_invoice(channel):

    if not bill_generated or not current_pdf:
        messagebox.showerror(
            "Error",
            "Generate PDF before sending"
        )
        return

    # Capture GUI values on the main thread
    pdf_path = current_pdf
    recipient = customer_email.get().strip()
    customer = customer_name.get().strip()
    phone = customer_phone.get().strip()
    bill = bill_no.get()
    amount = calculate_total()

    if channel in ("email", "both") and not recipient:
        messagebox.showerror("Error", "Enter customer email")
        return

    if channel in ("whatsapp", "both") and not phone:
        messagebox.showerror("Error", "Enter customer phone")
        return

    email_button.config(state="disabled")
    whatsapp_button.config(state="disabled")
    both_button.config(state="disabled")

    update_status(f"Sending {channel} invoice...")

    def worker():

        results = []

        if channel in ("email", "both"):

            try:
                send_email(
                    pdf_path,
                    recipient,
                    customer,
                    bill,
                    amount
                )

                results.append("Email: Sent successfully")

            except Exception as e:
                results.append(f"Email failed: {e}")

        if channel in ("whatsapp", "both"):

            try:
                send_whatsapp(
                    pdf_path,
                    phone,
                    bill
                )

                results.append(
                    "WhatsApp: Message submitted to Meta"
                )

            except Exception as e:
                results.append(f"WhatsApp failed: {e}")

        def finish():

            email_button.config(state="normal")
            whatsapp_button.config(state="normal")
            both_button.config(state="normal")

            update_status("Delivery process completed")

            messagebox.showinfo(
                "Invoice Delivery",
                "\n\n".join(results)
            )

        root.after(0, finish)

    threading.Thread(
        target=worker,
        daemon=True
    ).start()


# ==================================================
# SAVE PDF
# ==================================================

def save_pdf_as():

    if not bill_generated or not current_pdf:
        messagebox.showerror(
            "Error", "Generate PDF first"
        )
        return

    destination = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")],
        initialfile=os.path.basename(current_pdf)
    )

    if destination:
        import shutil
        shutil.copy2(current_pdf, destination)

        messagebox.showinfo(
            "Success", "PDF saved successfully"
        )


# ==================================================
# NEW BILL
# ==================================================

def clear_all():

    global bill_generated, current_pdf, bill_datetime

    if items:
        confirm = messagebox.askyesno(
            "New Bill",
            "Start a new bill? Current unsaved bill will be cleared."
        )

        if not confirm:
            return

    items.clear()

    for row in product_table.get_children():
        product_table.delete(row)

    customer_name.set("")
    customer_phone.set("")
    customer_email.set("")

    product_name.set("")
    product_rate.set("")
    product_qty.set("")

    bill_no.set(str(random.randint(100000, 999999)))

    preview.delete("1.0", tk.END)

    grand_total.set("Rs. 0.00")

    bill_generated = False
    current_pdf = None
    bill_datetime = None

    update_status("New bill ready")


# ==================================================
# GUI COMPONENTS
# ==================================================

# HEADER

header = tk.Frame(
    root,
    bg=BLUE,
    height=80
)

header.pack(fill="x")
header.pack_propagate(False)

tk.Label(
    header,
    text="  LJ",
    bg=BLUE,
    fg="white",
    font=("Arial", 23, "bold")
).pack(side="left", padx=10)

tk.Label(
    header,
    text=SHOP_NAME,
    bg=BLUE,
    fg=WHITE,
    font=("Arial", 21, "bold")
).pack(side="left", padx=10)

tk.Label(
    header,
    text="RETAIL BILLING DASHBOARD",
    bg=BLUE,
    fg="#BFDBFE",
    font=("Arial", 11, "bold")
).pack(side="right", padx=25)


# BODY

body = tk.Frame(root, bg=BG)
body.pack(fill="both", expand=True, padx=20, pady=15)


# SIDEBAR

sidebar = tk.Frame(
    body,
    bg=DARK,
    width=190
)

sidebar.pack(side="left", fill="y", padx=(0, 15))
sidebar.pack_propagate(False)

tk.Label(
    sidebar,
    text="MAIN MENU",
    bg=DARK,
    fg="#93C5FD",
    font=("Arial", 11, "bold")
).pack(pady=25)

def sidebar_button(text, command):

    tk.Button(
        sidebar,
        text=text,
        command=command,
        bg=DARK,
        fg=WHITE,
        activebackground=BLUE,
        activeforeground=WHITE,
        bd=0,
        anchor="w",
        font=("Arial", 11, "bold"),
        padx=20,
        pady=14,
        cursor="hand2"
    ).pack(fill="x")


# MAIN AREA

main = tk.Frame(body, bg=BG)
main.pack(side="left", fill="both", expand=True)


# CUSTOMER CARD

customer_card = tk.LabelFrame(
    main,
    text=" CUSTOMER INFORMATION ",
    bg=WHITE,
    fg=BLUE,
    font=("Arial", 12, "bold"),
    padx=15,
    pady=12
)

customer_card.pack(fill="x", pady=(0, 12))


def create_field(parent, label, variable, column):

    tk.Label(
        parent,
        text=label,
        bg=WHITE,
        fg=GRAY,
        font=("Arial", 10, "bold")
    ).grid(
        row=0,
        column=column,
        sticky="w",
        padx=10
    )

    entry = ttk.Entry(
        parent,
        textvariable=variable,
        width=25
    )

    entry.grid(
        row=1,
        column=column,
        padx=10,
        pady=8,
        sticky="ew"
    )

    return entry


create_field(
    customer_card, "Customer Name",
    customer_name, 0
)

create_field(
    customer_card, "Phone (+91)",
    customer_phone, 1
)

create_field(
    customer_card, "Email Address",
    customer_email, 2
)


# CONTENT

content = tk.Frame(main, bg=BG)
content.pack(fill="both", expand=True)

content.columnconfigure(0, weight=1)
content.columnconfigure(1, weight=1)
content.rowconfigure(0, weight=1)


# PRODUCT CARD

product_card = tk.LabelFrame(
    content,
    text=" PRODUCT MANAGEMENT ",
    bg=WHITE,
    fg=BLUE,
    font=("Arial", 12, "bold"),
    padx=12,
    pady=12
)

product_card.grid(
    row=0,
    column=0,
    sticky="nsew",
    padx=(0, 8)
)

product_card.columnconfigure(0, weight=1)
product_card.rowconfigure(2, weight=1)


product_inputs = tk.Frame(product_card, bg=WHITE)
product_inputs.grid(
    row=0,
    column=0,
    sticky="ew"
)

create_field(
    product_inputs, "Product",
    product_name, 0
)

create_field(
    product_inputs, "Rate",
    product_rate, 1
)

create_field(
    product_inputs, "Quantity",
    product_qty, 2
)


ttk.Button(
    product_card,
    text="+ ADD PRODUCT",
    command=add_item
).grid(
    row=1,
    column=0,
    sticky="w",
    pady=12
)


product_table = ttk.Treeview(
    product_card,
    columns=("name", "qty", "rate", "total"),
    show="headings"
)

for col, heading in [
    ("name", "Product"),
    ("qty", "Qty"),
    ("rate", "Rate"),
    ("total", "Total")
]:
    product_table.heading(col, text=heading)

product_table.column("name", width=140)
product_table.column("qty", width=55, anchor="center")
product_table.column("rate", width=85, anchor="e")
product_table.column("total", width=95, anchor="e")

product_table.grid(
    row=2,
    column=0,
    sticky="nsew"
)


ttk.Button(
    product_card,
    text="Remove Selected",
    command=remove_item
).grid(
    row=3,
    column=0,
    sticky="w",
    pady=8
)


# TOTAL CARD

total_card = tk.Frame(
    product_card,
    bg="#DCFCE7",
    padx=15,
    pady=15
)

total_card.grid(
    row=4,
    column=0,
    sticky="ew",
    pady=10
)

tk.Label(
    total_card,
    text="GRAND TOTAL",
    bg="#DCFCE7",
    fg=GREEN,
    font=("Arial", 12, "bold")
).pack(side="left")

tk.Label(
    total_card,
    textvariable=grand_total,
    bg="#DCFCE7",
    fg=GREEN,
    font=("Arial", 19, "bold")
).pack(side="right")


# INVOICE PREVIEW

preview_card = tk.LabelFrame(
    content,
    text=" INVOICE PREVIEW ",
    bg=WHITE,
    fg=BLUE,
    font=("Arial", 12, "bold"),
    padx=10,
    pady=10
)

preview_card.grid(
    row=0,
    column=1,
    sticky="nsew",
    padx=(8, 0)
)

preview_card.rowconfigure(0, weight=1)
preview_card.columnconfigure(0, weight=1)

preview = tk.Text(
    preview_card,
    bg="#F8FAFC",
    fg=DARK,
    font=("Consolas", 10),
    wrap="none",
    padx=12,
    pady=12
)

preview.grid(
    row=0,
    column=0,
    sticky="nsew"
)


# ACTION BUTTONS

action_bar = tk.Frame(main, bg=BG)
action_bar.pack(fill="x", pady=12)


def action_button(parent, text, command, bg):

    return tk.Button(
        parent,
        text=text,
        command=command,
        bg=bg,
        fg=WHITE,
        activebackground=bg,
        activeforeground=WHITE,
        font=("Arial", 10, "bold"),
        padx=13,
        pady=11,
        bd=0,
        cursor="hand2"
    )


action_button(
    action_bar,
    "GENERATE PDF",
    generate_bill,
    BLUE
).pack(side="left", padx=4)

action_button(
    action_bar,
    "SAVE PDF",
    save_pdf_as,
    GRAY
).pack(side="left", padx=4)

email_button = action_button(
    action_bar,
    "SEND EMAIL",
    lambda: deliver_invoice("email"),
    "#2563EB"
)

email_button.pack(side="left", padx=4)

whatsapp_button = action_button(
    action_bar,
    "SEND WHATSAPP",
    lambda: deliver_invoice("whatsapp"),
    GREEN
)

whatsapp_button.pack(side="left", padx=4)

both_button = action_button(
    action_bar,
    "SEND BOTH",
    lambda: deliver_invoice("both"),
    "#7C3AED"
)

both_button.pack(side="left", padx=4)

action_button(
    action_bar,
    "NEW BILL",
    clear_all,
    RED
).pack(side="right", padx=4)


# SIDEBAR ACTIONS

sidebar_button("  New Bill", clear_all)

sidebar_button(
    "  Generate Invoice",
    generate_bill
)

sidebar_button(
    "  Send Email",
    lambda: deliver_invoice("email")
)

sidebar_button(
    "  Send WhatsApp",
    lambda: deliver_invoice("whatsapp")
)

sidebar_button(
    "  Save Invoice",
    save_pdf_as
)


# STATUS BAR

tk.Label(
    root,
    textvariable=status,
    bg="#E2E8F0",
    fg=DARK,
    anchor="w",
    padx=15,
    pady=9,
    font=("Arial", 9)
).pack(fill="x")


# RUN

root.mainloop()
