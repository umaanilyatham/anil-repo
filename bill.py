from tkinter import *
from tkinter import messagebox
import random
from datetime import datetime
import os

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors


# ================= WINDOW =================
root = Tk()
root.title("Billing System")
root.geometry("1280x730")
root.config(bg="white")

# ================= VARIABLES =================
customer_name = StringVar()
customer_phone = StringVar()
product_name = StringVar()
Rate = IntVar()
Qty = IntVar()
bill_no = StringVar()

bill_no.set(str(random.randint(1000, 9999)))

items = []
bill_generated = False


# ================= FUNCTIONS =================
def additem():
    if product_name.get() == "":
        messagebox.showerror("Error", "Enter product name")
        return

    rate = Rate.get()
    qty = Qty.get()

    if rate <= 0 or qty <= 0:
        messagebox.showerror("Error", "Rate & Quantity must be greater than 0")
        return

    total = rate * qty
    items.append((product_name.get(), qty, rate, total))

    textarea.insert(END, f"\n{product_name.get()}\t\t{qty}\t₹{total}")

    product_name.set("")
    Rate.set(0)
    Qty.set(0)


def generate_bill():
    global bill_generated
    bill_generated = True

    textarea.delete(1.0, END)

    now = datetime.now()
    date = now.strftime("%d-%m-%Y")
    time = now.strftime("%I:%M %p")

    textarea.insert(END, "\t\tAMRUTHA AGENCY RETAILS\n")
    textarea.insert(END, "\t\t----------------------\n")
    textarea.insert(END, f"\nBill No : {bill_no.get()}")
    textarea.insert(END, f"\nDate    : {date}")
    textarea.insert(END, f"\nTime    : {time}")
    textarea.insert(END, f"\nCustomer: {customer_name.get()}")
    textarea.insert(END, f"\nPhone   : {customer_phone.get()}")
    textarea.insert(END, "\n========================================")
    textarea.insert(END, "\nProduct\t\tQty\tTotal")
    textarea.insert(END, "\n========================================")

    grand_total = 0
    for product, qty, rate, total in items:
        textarea.insert(END, f"\n{product}\t\t{qty}\t₹{total}")
        grand_total += total

    textarea.insert(END, "\n========================================")
    textarea.insert(END, f"\nGrand Total:\t\t₹ {grand_total}")
    textarea.insert(END, "\n========================================")


def save_pdf():
    if not bill_generated:
        messagebox.showerror("Error", "Generate bill first")
        return

    base_path = os.path.dirname(os.path.abspath(__file__))
    left_img = os.path.join(base_path, "vin.jpg")
    right_img = os.path.join(base_path, "saibaba.jpg")

    filename = f"Invoice_{bill_no.get()}.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    # ===== GOD IMAGES =====
    c.drawImage(left_img, 40, height - 100, 80, 80, mask='auto')
    c.drawImage(right_img, width - 120, height - 100, 80, 80, mask='auto')

    # ===== HEADING =====
    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(colors.darkblue)
    c.drawCentredString(width / 2, height - 80, "AMRUTHA AGENCY RETAILS")

    c.setFont("Helvetica", 12)
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2, height - 105, "Billing Invoice")
    c.line(40, height - 115, width - 40, height - 115)

    now = datetime.now()
    y = height - 150
    c.setFont("Helvetica", 11)
    c.drawString(50, y, f"Bill No : {bill_no.get()}")
    c.drawString(350, y, f"Date : {now.strftime('%d-%m-%Y')}")
    y -= 20
    c.drawString(50, y, f"Customer : {customer_name.get()}")
    c.drawString(350, y, f"Time : {now.strftime('%I:%M %p')}")
    y -= 20
    c.drawString(50, y, f"Phone : {customer_phone.get()}")
    y -= 40

    # ===== TABLE HEADER =====
    c.setFillColor(colors.lightgrey)
    c.rect(40, y, width - 80, 25, fill=1)
    c.setFillColor(colors.black)

    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y + 7, "Product")
    c.drawString(280, y + 7, "Qty")
    c.drawString(360, y + 7, "Total")

    y -= 25
    c.setFont("Helvetica", 11)

    grand_total = 0
    for product, qty, rate, total in items:
        c.drawString(50, y, product)
        c.drawString(290, y, str(qty))
        c.drawString(370, y, f"₹ {total}")
        grand_total += total
        y -= 20

    y -= 20
    c.setFont("Helvetica-Bold", 14)
    c.drawString(300, y, "Grand Total :")
    c.drawString(430, y, f"₹ {grand_total}")

    y -= 60
    c.setFont("Helvetica-Oblique", 10)
    c.drawCentredString(width / 2, y, "🙏 Thank you for shopping with us 🙏")

    c.save()
    messagebox.showinfo("Success", f"PDF saved successfully\n{filename}")


def clear_all():
    textarea.delete(1.0, END)
    items.clear()
    customer_name.set("")
    customer_phone.set("")
    product_name.set("")
    Rate.set(0)
    Qty.set(0)


# ================= GUI =================
Label(root, text="AMRUTHA AGENCY BILLING SYSTEM",
      font=("times new roman", 30, "bold"),
      bg="blue", fg="white").pack(fill=X)

# Customer Frame
f1 = LabelFrame(root, text="Customer Details",
                font=("times new roman", 18, "bold"),
                fg="gold", bg="blue", bd=10)
f1.place(x=0, y=80, relwidth=1)

Label(f1, text="Name", bg="blue", fg="white",
      font=("times new roman", 18)).grid(row=0, column=0)
Entry(f1, textvariable=customer_name,
      font="arial 15", width=15).grid(row=0, column=1, padx=10)

Label(f1, text="Phone", bg="blue", fg="white",
      font=("times new roman", 18)).grid(row=0, column=2)
Entry(f1, textvariable=customer_phone,
      font="arial 15", width=15).grid(row=0, column=3, padx=10)

# Product Frame
f2 = LabelFrame(root, text="Product Details",
                font=("times new roman", 18, "bold"),
                fg="gold", bg="blue", bd=10)
f2.place(x=20, y=180, width=630, height=500)

Label(f2, text="Product", bg="blue", fg="white",
      font=("times new roman", 18)).grid(row=0, column=0)
Entry(f2, textvariable=product_name,
      font="arial 15", width=15).grid(row=0, column=1)

Label(f2, text="Rate", bg="blue", fg="white",
      font=("times new roman", 18)).grid(row=1, column=0)
Entry(f2, textvariable=Rate,
      font="arial 15", width=15).grid(row=1, column=1)

Label(f2, text="Quantity", bg="blue", fg="white",
      font=("times new roman", 18)).grid(row=2, column=0)
Entry(f2, textvariable=Qty,
      font="arial 15", width=15).grid(row=2, column=1)

Button(f2, text="Add Item", command=additem,
       bg="green", fg="white",
       font="arial 12 bold", width=15).grid(row=3, column=0, pady=10)

Button(f2, text="Generate Bill", command=generate_bill,
       bg="orange", fg="white",
       font="arial 12 bold", width=15).grid(row=3, column=1)

Button(f2, text="Save PDF", command=save_pdf,
       bg="purple", fg="white",
       font="arial 12 bold", width=15).grid(row=4, column=0)

Button(f2, text="Clear", command=clear_all,
       bg="red", fg="white",
       font="arial 12 bold", width=15).grid(row=4, column=1)

# Bill Area
f3 = Frame(root, bd=10, relief=GROOVE)
f3.place(x=700, y=180, width=500, height=500)

Label(f3, text="Bill Preview",
      font="arial 15 bold").pack(fill=X)

textarea = Text(f3, font="arial 12")
textarea.pack(fill=BOTH, expand=True)

root.mainloop()
