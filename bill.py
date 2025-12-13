from tkinter import *
import random
from tkinter import messagebox

root = Tk()
root.title("Billing System")
root.geometry("1280x730")

#=========VARIABLES=====
customer_name = StringVar()
customer_phone = StringVar()
Email_Id = StringVar()
product_name = StringVar()
Rate = IntVar()
Qty = IntVar()
bill_no = StringVar()

x = random.randint(1, 9999)
bill_no.set(str(x))

l = []   # list to store item totals
items_list = []  # STORE EACH ITEM (name, qty, rate, total)


#========= FUNCTIONS =========
def welcome():
    textarea.delete(1.0, END)
    textarea.insert(END, "\tWELCOME ANIL RETAILS")
    textarea.insert(END, f"\n\nBill Number :\t\t{bill_no.get()}")
    textarea.insert(END, f"\nCustomer Name:\t\t{customer_name.get()}")
    textarea.insert(END, f"\nPhone Number:\t\t{customer_phone.get()}")
    textarea.insert(END, "\n====================================")
    textarea.insert(END, "\nProduct\t\tQty\tRate\tTotal")
    textarea.insert(END, "\n====================================")
    textarea.configure(font='arial 15 bold')


def additem():
    if product_name.get() == "":
        messagebox.showerror("Error", "Please enter product name")
        return

    qty = Qty.get()
    rate = Rate.get()
    total = qty * rate

    l.append(total)
    items_list.append([product_name.get(), qty, rate, total])

    textarea.insert(END, f"\n{product_name.get()}\t\t{qty}\t{rate}\t{total}")


def gbill():
    welcome()

    # PRINT ALL ITEMS
    for item in items_list:
        textarea.insert(END, f"\n{item[0]}\t\t{item[1]}\t{item[2]}\t{item[3]}")

    textarea.insert(END, "\n====================================")
    textarea.insert(END, f"\nTotal Payable Amount:\t\t{sum(l)}")
    textarea.insert(END, "\n====================================")


def clear():
    product_name.set("")
    Rate.set(0)
    Qty.set(0)
    textarea.delete(1.0, END)
    l.clear()
    items_list.clear()


def exit_app():
    root.destroy()


#==================== GUI ==================#
title = Label(root, text="AMURUTHA AGENCY BILLING SYSTEM",
              bg="blue", fg="white", font=("times new roman", 30, "bold"))
title.pack(fill=X)

# Customer Frame
f1 = LabelFrame(root, text="Customer Details", font=("times new roman", 18, "bold"),
                fg="gold", bg="blue", relief=GROOVE, bd=10)
f1.place(x=0, y=80, relwidth=1)

Label(f1, text="Customer Name", font=("times new roman", 18, "bold"),
      bg="blue", fg="white").grid(row=0, column=0, padx=10, pady=5)
Entry(f1, width=15, textvariable=customer_name, font="arial 15",
      bd=5, relief=SUNKEN).grid(row=0, column=1, padx=10, pady=5)

Label(f1, text="Phone No:", font=("times new roman", 18, "bold"),
      bg="blue", fg="white").grid(row=0, column=2, padx=10, pady=5)
Entry(f1, width=15, textvariable=customer_phone, font="arial 15",
      bd=5, relief=SUNKEN).grid(row=0, column=3, padx=10, pady=5)

Label(f1, text="Email Id:", font=("times new roman", 18, "bold"),
      bg="blue", fg="white").grid(row=0, column=4, padx=10, pady=5)
Entry(f1, width=15, textvariable=Email_Id, font="arial 15",
      bd=5, relief=SUNKEN).grid(row=0, column=5, padx=10, pady=5)


# Product Frame
f2 = LabelFrame(root, text="Product Details", font=("times new roman", 18, "bold"),
                fg="gold", bg="blue", relief=GROOVE, bd=10)
f2.place(x=20, y=180, width=630, height=500)

Label(f2, text="Product Name:", font=("times new roman", 18, "bold"),
      bg="blue", fg="white").grid(row=0, column=0, padx=10, pady=10)
Entry(f2, width=15, textvariable=product_name, font="arial 15",
      bd=5, relief=SUNKEN).grid(row=0, column=1, padx=30, pady=20)

Label(f2, text="Rate:", font=("times new roman", 18, "bold"),
      bg="blue", fg="white").grid(row=1, column=0, padx=10, pady=10)
Entry(f2, width=15, textvariable=Rate, font="arial 15",
      bd=5, relief=SUNKEN).grid(row=1, column=1, padx=30, pady=20)

Label(f2, text="Quantity:", font=("times new roman", 18, "bold"),
      bg="blue", fg="white").grid(row=2, column=0, padx=10, pady=10)
Entry(f2, width=15, textvariable=Qty, font="arial 15",
      bd=5, relief=SUNKEN).grid(row=2, column=1, padx=30, pady=20)

# Buttons
Button(f2, text="Add Item", command=additem, width=15, bd=5,
       bg="green", fg="white", font="arial 12 bold").grid(row=3, column=0, pady=10)

Button(f2, text="Generate Bill", command=gbill, width=15, bd=5,
       bg="orange", fg="white", font="arial 12 bold").grid(row=3, column=1, pady=10)

Button(f2, text="Clear", command=clear, width=15, bd=5,
       bg="red", fg="white", font="arial 12 bold").grid(row=4, column=0, pady=10)

Button(f2, text="Exit", command=exit_app, width=15, bd=5,
       bg="black", fg="white", font="arial 12 bold").grid(row=4, column=1, pady=10)


# Bill Area
f3 = Frame(root, bd=10, relief=GROOVE)
f3.place(x=700, y=180, width=500, height=500)

Label(f3, text="Bill Area", font="arial 15 bold",
      bd=7, relief=GROOVE).pack(fill=X)

scroll_y = Scrollbar(f3, orient=VERTICAL)
textarea = Text(f3, yscrollcommand=scroll_y)
scroll_y.pack(side=RIGHT, fill=Y)
scroll_y.config(command=textarea.yview)
textarea.pack(fill=BOTH, expand=True)

root.mainloop()
