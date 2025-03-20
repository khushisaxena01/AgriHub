# backend database - login, main menu & password verification

import tkinter as tk
from tkinter import messagebox
import mysql.connector

# Create MySQL Database
def create_database():
    conn = mysql.connector.connect(host="localhost", user="root", password="Sahu@200525")
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS farmers_db")
    cursor.execute("USE farmers_db")
    cursor.execute("""CREATE TABLE IF NOT EXISTS farmers (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            phone VARCHAR(10) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Connect to Database
def get_db_connection():
    return mysql.connector.connect(host="localhost", user="root", password="Sahu@200525", database="farmers_db")

# Show Signup Frame
def show_signup():
    main_frame.pack_forget()
    signup_frame.pack()

# Show Login Frame
def show_login():
    main_frame.pack_forget()
    login_frame.pack()

# Back to Main Menu
def show_main():
    signup_frame.pack_forget()
    login_frame.pack_forget()
    main_frame.pack()

# Signup Function with Password Confirmation
def signup():
    name = entry_signup_name.get()
    phone = entry_signup_phone.get()
    password = entry_signup_password.get()
    confirm_password = entry_signup_confirm_password.get()

    if not name or not phone or not password or not confirm_password:
        messagebox.showerror("Error", "All fields are required")
        return

    if len(phone) != 10 or not phone.isdigit():
        messagebox.showerror("Error", "Phone number must be 10 digits")
        return

    if password != confirm_password:
        messagebox.showerror("Error", "Passwords do not match")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO farmers (name, phone, password) VALUES (%s, %s, SHA2(%s, 256))", 
                       (name, phone, password))
        conn.commit()
        messagebox.showinfo("Success", "Signup Successful")
        show_main()
    except mysql.connector.IntegrityError:
        messagebox.showerror("Error", "Phone number already registered")
    finally:
        conn.close()

# Login Function
def login():
    phone = entry_login_phone.get()
    password = entry_login_password.get()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM farmers WHERE phone = %s AND password = SHA2(%s, 256)", (phone, password))
    farmer = cursor.fetchone()
    conn.close()

    if farmer:
        messagebox.showinfo("Success", "Login Successful")
    else:
        messagebox.showerror("Error", "Invalid Phone Number or Password")

# Initialize Database
create_database()

# GUI Setup
tk_root = tk.Tk()
tk_root.title("Farmer Login & Signup")
tk_root.geometry("400x400")
tk_root.configure(bg="white")

# Button Style
button_style = {
    "bg": "#4CAF50", "fg": "white", "font": ("Arial", 12, "bold"), "width": 15, "height": 1, "bd": 2, "relief": "solid"
}

# Main Frame
main_frame = tk.Frame(tk_root, bg="white")
tk.Label(main_frame, text="Welcome to Farmer Portal", font=("Arial", 16, "bold"), bg="white").pack(pady=10)
tk.Button(main_frame, text="Signup", command=show_signup, **button_style).pack(pady=5)
tk.Button(main_frame, text="Login", command=show_login, **button_style).pack(pady=5)
main_frame.pack(expand=True)

# Signup Frame
signup_frame = tk.Frame(tk_root, bg="white")
tk.Label(signup_frame, text="Farmer Signup", font=("Arial", 14, "bold"), bg="white").pack(pady=10)
tk.Label(signup_frame, text="Name", bg="white").pack()
entry_signup_name = tk.Entry(signup_frame, width=30)
entry_signup_name.pack(pady=5)
tk.Label(signup_frame, text="Phone Number", bg="white").pack()
entry_signup_phone = tk.Entry(signup_frame, width=30)
entry_signup_phone.pack(pady=5)
tk.Label(signup_frame, text="Password", bg="white").pack()
entry_signup_password = tk.Entry(signup_frame, show="*", width=30)
entry_signup_password.pack(pady=5)
tk.Label(signup_frame, text="Confirm Password", bg="white").pack()
entry_signup_confirm_password = tk.Entry(signup_frame, show="*", width=30)
entry_signup_confirm_password.pack(pady=5)
tk.Button(signup_frame, text="Signup", command=signup, **button_style).pack(pady=5)
tk.Button(signup_frame, text="Back", command=show_main, **button_style).pack(pady=5)

# Login Frame
login_frame = tk.Frame(tk_root, bg="white")
tk.Label(login_frame, text="Farmer Login", font=("Arial", 14, "bold"), bg="white").pack(pady=10)
tk.Label(login_frame, text="Phone Number", bg="white").pack()
entry_login_phone = tk.Entry(login_frame, width=30)
entry_login_phone.pack(pady=5)
tk.Label(login_frame, text="Password", bg="white").pack()
entry_login_password = tk.Entry(login_frame, show="*", width=30)
entry_login_password.pack(pady=5)
tk.Button(login_frame, text="Login", command=login, **button_style).pack(pady=5)
tk.Button(login_frame, text="Back", command=show_main, **button_style).pack(pady=5)

tk_root.mainloop()