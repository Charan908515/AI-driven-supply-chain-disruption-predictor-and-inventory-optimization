
import tkinter as tk
from tkinter import messagebox
from tkinter.ttk import LabelFrame, Label, Button, Entry, Frame, Scrollbar, Style
from electric_batteries import *
from ttkthemes import themed_tk
from database import Database
from convertToExcel import convert, calc_profit
import mysql.connector
import os
import pandas as pd

if __name__ == '__main__':

    db = Database("products.db")
    def populate_list():
        product_list_listbox.delete(0, tk.END)
        for num, row in enumerate(db.fetch_all_rows()):
            string = ""
            for i in row:
                string = string + "  |  " + str(i)
            string = str(num + 1) + string
            product_list_listbox.insert(tk.END, string)

    # Function to bind listbox
    def select_item(event):
        try:
            global selected_item
            selection = product_list_listbox.curselection()
            if not selection:
                return  # No item selected
            index = product_list_listbox.curselection()[0]
            selected_item = product_list_listbox.get(index)
            selected_item = selected_item.split(" | ")

            # Fetch the row from the database
            selected_item = db.fetch_by_product_id(selected_item[1])  # Expecting a single tuple
            if not selected_item:
                print("No matching product found.")
                return

            # Populate the entry fields
            clear_input()
            product_id_entry.insert(0, selected_item[0])  # Access tuple values directly
            month_id_entry.insert(0, selected_item[1])
            incoming_id_entry.insert(0, selected_item[2])
            outgoing_id_entry.insert(0, selected_item[3])
            country_id_entry.insert(0, selected_item[4])
            stock_id_entry.insert(0, selected_item[5])
        except IndexError:
            print("Error: No item selected or listbox is empty.")
        except Exception as e:
            print(f"Unexpected error: {e}")


    def generate_alerts():
    # Load the CSV data
        products_database =db.fetch_all_rows()
        data=pd.DataFrame(products_database,columns=["ID","Month","incoming","outgoing","Country","stock_level"])
        risk_data=pd.read_csv("Risk_and_Sentiment_Results.csv")
        risk_data['Published At'] = pd.to_datetime(risk_data['Published At']).dt.date


        # Define thresholds and conditions
        warehouse_capacity_threshold = 0.8  # 80% capacity considered high
        risk_threshold = "low"  # Risk levels: Low, Medium, High
        sentiment_threshold = "negative"  # Sentiment: Positive, Neutral, Negative

        alerts = []
        warehouse_capacity=10000
        for product_index,row in data.iterrows():
            for risk_index,risk in risk_data.iterrows():
                if row["Country"]==risk["country"]:
            # Calculate warehouse utilization
                    utilization = row['incoming'] /warehouse_capacity
                    # Analyze risk factors and sentiment
                    if utilization > warehouse_capacity_threshold or risk_threshold in risk['Risk Analysis']:
                        if sentiment_threshold in risk['Sentiment']:
                            alerts.append((row['Month'], "SELL", f"High utilization ({utilization:.2f}), {risk['Risk Analysis']} risk, {risk['Sentiment']} sentiment"))
                        else:
                            alerts.append((risk['Month'], "MONITOR", f"High utilization ({utilization:.2f}) with {risk['Risk Analysis']} risk"))
                    elif utilization < 0.4:  # If utilization is very low
                        alerts.append((risk['Month'], "BUY", f"Low utilization ({utilization:.2f}), consider buying material"))

        return alerts
    conn = mysql.connector.connect(
        host="127.0.0.1",  # For example: "localhost" or IP address
        user="root",       # Your MySQL username
        password="charan#30",  # Your MySQL password
        database="inventory_management"  # Database name
    )
    cursor = conn.cursor()

    # Create tables if they don't exist, including "Published At" for adjustments
   
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS adjusted_inventory (
        country_name VARCHAR(255) PRIMARY KEY,
        stock_level INT,
        stock_adjusted INT,
        adjustment FLOAT,
        `Published At` DATE
    )
    """)
    def adjust_stock_db(title, risk_level, published_at):
        
        products_database =db.fetch_all_rows()
        data=pd.DataFrame(products_database,columns=["ID","Month","incoming","outgoing","Country","stock_level"])
      
        for index,row in data.iterrows():
            if row["Country"].lower() in title.lower():
                # Fetch stock level
                stock_level = row["stock_level"]

                # Adjust stock
                if risk_level == 'High':
                    stock_adjustment = stock_level * -0.20  # Decrease by 20%
                elif risk_level == 'Medium':
                    stock_adjustment = stock_level * 0.0  # No change
                elif risk_level == 'Low':
                    stock_adjustment = stock_level * 0.05  # Increase by 5%
                else:
                    stock_adjustment = 0

                # Calculate the new stock level after adjustment
                new_stock = int(stock_level + stock_adjustment)

                # Check if the country already has an adjustment in adjusted_inventory
                cursor.execute("""
                    SELECT `Published At` FROM adjusted_inventory 
                    WHERE country_name = %s
                """, (row["country"]))
                result = cursor.fetchone()

                # Insert or update based on the Published At date
                if result:
                    existing_date = result[0]
                    if published_at > existing_date:
                        # Update the existing entry if the new date is later
                        cursor.execute("""
                            UPDATE adjusted_inventory
                            SET stock_level = %s, stock_adjusted = %s, adjustment = %s, `Published At` = %s
                            WHERE country_name = %s
                        """, (stock_level, new_stock, stock_adjustment, published_at, row["country"]))
                else:
                    # Insert a new entry if no existing record
                    cursor.execute("""
                        INSERT INTO adjusted_inventory (country_name, stock_level, stock_adjusted, adjustment, `Published At`)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (row["country"], stock_level, new_stock, stock_adjustment, published_at))
                conn.commit()
            else:
                continue

                return stock_adjustment
    risk_data=pd.read_csv("Risk_and_Sentiment_Results.csv")
    risk_data['Published At'] = pd.to_datetime(risk_data['Published At']).dt.date

    for _, row in risk_data.iterrows():
        adjustment = adjust_stock_db(row['Title'], row['Risk Analysis'], row['Published At'])
        cursor.execute("""
        INSERT INTO risk_data (title, risk_level, stock_adjustment, `Published At`)
        VALUES (%s, %s, %s, %s)
    """, (row['Title'], row['Risk Level'], adjustment, row['Published At']))
    conn.commit()

# Fetch updated adjusted inventory for review
    cursor.execute("SELECT * FROM adjusted_inventory")
    updated_adjusted_inventory = cursor.fetchall()

# Display the adjusted inventory
    print(pd.DataFrame(updated_adjusted_inventory, columns=["Country", "Stock Level", "Stock Adjusted", "Adjustment", "Published At"]))

# Close the database connection
    conn.close()
    # Create main window with using themed_tk
    # provides themed widgets and window styles for Tkinter
    root = themed_tk.ThemedTk()
    root.set_theme("scidpurple")

    root.title("AI Driven Supply Chain and  Inventory Management System")
    width = 1080
    height = 700
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    # get the dimensions of the screen, in pixels. The window is then positioned in the center of the screen by dividing these dimensions by 2 and subtracting half the width and height of the window.
    root.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    root.columnconfigure(0, weight=1)
   # im = Image.open("C:\Users\nchar\Desktop\infosys-project\images\icon.png")
   # icon = ImageTk.PhotoImage(im)
    # Set the window icon using the PhotoImage object
    #root.wm_iconphoto(True, icon)

    entry_frame = LabelFrame(root, text="Enter Product Details")
    # Product ID

    product_id_var = tk.StringVar()
    product_id_label = Label(entry_frame, text="Product ID: ")
    product_id_label.grid(row=0, column=0, sticky="w", padx=10)
    product_id_entry = Entry(entry_frame, textvariable=product_id_var)
    product_id_entry.grid(row=0, column=1)


    month_id_var = tk.StringVar()
    month_id_label = Label(entry_frame, text="Month: ")
    month_id_label.grid(row=1, column=0, sticky="w", padx=10)
    month_id_entry = Entry(entry_frame, textvariable=month_id_var)
    month_id_entry.grid(row=1, column=1)

    # incoming stock
    incoming_id_var = tk.StringVar()
    incoming_id_label = Label(entry_frame, text="Incoming Stock: ")
    incoming_id_label.grid(row=1, column=2, sticky="w", padx=10)
    incoming_id_entry = Entry(entry_frame, textvariable= incoming_id_var)
    incoming_id_entry.grid(row=1, column=3)

    # outgoing stock
    outgoing_id_var = tk.StringVar()
    outgoing_id_label = Label(entry_frame, text="Outgoing Stock: ")
    outgoing_id_label.grid(row=0, column=2, sticky="w", padx=10)
    outgoing_id_entry = Entry(entry_frame, textvariable=outgoing_id_var)
    outgoing_id_entry.grid(row=0, column=3)

    # country
    country_id_var = tk.StringVar()
    country_id_label = Label(entry_frame, text="Country: ")
    country_id_label.grid(row=0, column=4, sticky="w", padx=10)
    country_id_entry = Entry(entry_frame, textvariable=country_id_var)
    country_id_entry.grid(row=0, column=5)


    # stock level
    stock_id_var = tk.StringVar()
    stock_id_label = Label(entry_frame, text="Stock_level: ")
    stock_id_label.grid(row=1, column=4, sticky="w", padx=10)
    stock_id_entry = Entry(entry_frame, textvariable=stock_id_var)
    stock_id_entry.grid(row=1, column=5)


    # ****************************************** #

    # Product List
    # frame containing product listing and scrollbar
    listing_frame = Frame(root, borderwidth=1, relief="raised")
    product_list_listbox = tk.Listbox(listing_frame)
    product_list_listbox.grid(row=0, column=0, padx=10, pady=5, sticky="we")
    # binding list box to show selected items in the entry fields.
    product_list_listbox.bind("<<ListboxSelect>>", select_item)

    # Create ScrollBar
    scroll_bar = Scrollbar(listing_frame)
    scroll_bar.config(command=product_list_listbox.yview)
    scroll_bar.grid(row=0, column=1, sticky="ns")

    # Attach Scrollbar to Listbox
    product_list_listbox.config(yscrollcommand=scroll_bar.set)

    # =========================#

    # Create Statusbar using Label widget onto root
    statusbar_label = tk.Label(
        root, text="Status: ", bg="#ffb5c5", anchor="w", font=("arial", 10)
    )
    statusbar_label.grid(row=3, column=0, sticky="we", padx=10)
    # ========================#

    # Button Functions
    def add_item():
        if (product_id_var.get()==""
                or month_id_var.get() == ""
                or incoming_id_var.get() == ""
                or outgoing_id_var.get() == ""
                or country_id_var.get() == ""
                or stock_id_var.get() == ""
                
           
        ):
            messagebox.showerror(title="Required Fields", message="Please enter all fields")
            return

        db.insert(
            product_id_var.get(),
            month_id_var.get(),
            incoming_id_var.get(),
            outgoing_id_var.get(),
            country_id_var.get(),
            stock_id_var.get() 

           
        )
        clear_input()
        populate_list()
        statusbar_label["text"] = "Status: Product added successfully"
        statusbar_label.config(bg='green',fg='white')


    def update_item():
        if(     product_id_var.get() !=""
                and month_id_var.get() != ""
                and incoming_id_var.get() != ""
                and outgoing_id_var.get() != ""
                and country_id_var.get() != ""
                and stock_id_var.get() != ""
               ):
            db.update(
                selected_item[0],
                product_id_var.get(),
                month_id_var.get(),
                incoming_id_var.get(),
                outgoing_id_var.get(),
                country_id_var.get(),
                stock_id_var.get()
            )
            populate_list()
            statusbar_label["text"] = "Status: Product updated successfully"
            statusbar_label.config(bg='green',fg='white')
            return
        messagebox.showerror(title="Required Fields", message="Please enter all fields")
        statusbar_label["text"] = "Please enter all fields"
        statusbar_label.config(bg='red', fg='white')

    def remove_item():
        db.remove(selected_item[0])
        clear_input()
        populate_list()
        statusbar_label["text"] = "Status: Product removed from the list successfully"
        statusbar_label.config(bg='green', fg='white')

    def clear_input():
        product_id_entry.delete(0, tk.END)
        month_id_entry.delete(0, tk.END)
        incoming_id_entry.delete(0,tk.END)
        outgoing_id_entry.delete(0,tk.END)
        country_id_entry.delete(0,tk.END)
        stock_id_entry.delete(0,tk.END)
     


    def export_to_excel():
        convert()
        calc_profit()
        statusbar_label["text"] = f"Status: Excel file created in {os.getcwd()}"
        statusbar_label.config(bg='green', fg='white')

    # Buttons
    button_frame = Frame(root, borderwidth=2, relief="groove")

    add_item_btn = Button(button_frame, text="Add item", command=add_item)
    add_item_btn.grid(row=0, column=0, sticky="we", padx=10, pady=5)

    remove_item_btn = Button(button_frame, text="Remove item", command=remove_item)
    remove_item_btn.grid(row=0, column=1, sticky="we", padx=10, pady=5)

    update_item_btn = Button(button_frame, text="Update item", command=update_item)
    update_item_btn.grid(row=0, column=2, sticky="we", padx=10, pady=5)

    clear_item_btn = Button(button_frame, text="Clear Input", command=clear_input)
    clear_item_btn.grid(row=0, column=3, sticky="we", padx=10, pady=5)

    export_to_excel_btn = Button(
        button_frame, text="Export To Excel", command=export_to_excel
    )
    export_to_excel_btn.grid(row=0, column=4, sticky="we", padx=10, pady=5)

    entry_frame.grid(row=0, column=0, sticky="we", padx=10, pady=5)
    button_frame.grid(row=1, column=0, sticky="we", padx=10, pady=5)
    button_frame.grid_columnconfigure(0, weight=1)
    button_frame.grid_columnconfigure(1, weight=1)
    button_frame.grid_columnconfigure(2, weight=1)
    button_frame.grid_columnconfigure(3, weight=1)
    button_frame.grid_columnconfigure(4, weight=1)
    listing_frame.grid(row=2, column=0, sticky="we", padx=10)
    listing_frame.grid_columnconfigure(0, weight=2)

    populate_list()

    root.mainloop()
