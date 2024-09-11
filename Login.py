import tkinter as tk
from tkinter import messagebox, ttk
from database import connect_to_db
from datetime import datetime, timedelta
from search import setup_search_tab

def open_login_window():
    """Open the login window."""
    login_window = tk.Tk()
    login_window.title("Login")

    tk.Label(login_window, text="Username:").pack(pady=5)
    username_entry = tk.Entry(login_window)
    username_entry.pack(pady=5)

    tk.Label(login_window, text="Password:").pack(pady=5)
    password_entry = tk.Entry(login_window, show="*")
    password_entry.pack(pady=5)

    tk.Button(login_window, text="Login", command=lambda: login_action(username_entry.get(), password_entry.get(), login_window)).pack(pady=10)
    tk.Button(login_window, text="Register", command=open_register_window).pack(pady=5)
    tk.Button(login_window, text="Guest Mode", command=lambda: open_search_window(None, 'guest')).pack(pady=5)
    
    login_window.mainloop()

def login_action(username, password, login_window):
    """Authenticate the user and handle the result."""
    conn = connect_to_db()
    if conn is None:
        messagebox.showerror("Database Error", "Unable to connect to the database.")
        return

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM tblUser WHERE Username=? AND PasswordHash=?", (username, password))
        user = cursor.fetchone()
        if user:
            role = user[4]  # Assuming role is in column 4
            if role == 'admin':
                open_admin_window()
            else:
                open_search_window(username, role)
            login_window.destroy()
        else:
            messagebox.showerror("Login Error", "Invalid username or password.")
    except Exception as e:
        messagebox.showerror("Query Error", f"An error occurred: {e}")
    finally:
        conn.close()

def open_register_window():
    """Open the registration window."""
    register_window = tk.Tk()
    register_window.title("Register")

    tk.Label(register_window, text="Username:").pack(pady=5)
    reg_username_entry = tk.Entry(register_window)
    reg_username_entry.pack(pady=5)

    tk.Label(register_window, text="Email:").pack(pady=5)
    reg_email_entry = tk.Entry(register_window)
    reg_email_entry.pack(pady=5)

    tk.Label(register_window, text="Password:").pack(pady=5)
    reg_password_entry = tk.Entry(register_window, show="*")
    reg_password_entry.pack(pady=5)

    tk.Button(register_window, text="Register", command=lambda: register_action(reg_username_entry.get(), reg_email_entry.get(), reg_password_entry.get(), register_window)).pack(pady=10)
    
    register_window.mainloop()

def register_action(username, email, password, register_window):
    """Handle user registration."""
    conn = connect_to_db()
    if conn is None:
        messagebox.showerror("Database Error", "Unable to connect to the database.")
        return

    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO tblUser (Username, Email, PasswordHash, Role, ValidUntil) VALUES (?, ?, ?, 'member', ?)",
                       (username, email, password, datetime.now().date() + timedelta(days=365)))  # Default to 1 year validity
        conn.commit()
        messagebox.showinfo("Registration Successful", "You have successfully registered.")
        register_window.destroy()
    except Exception as e:
        messagebox.showerror("Registration Error", f"An error occurred: {e}")
    finally:
        conn.close()

def open_search_window(username, role):
    """Open the search window."""
    search_window = tk.Tk()
    search_window.title("Search Books")

    tab_control = ttk.Notebook(search_window)
    search_tab = ttk.Frame(tab_control)
    reservation_tab = ttk.Frame(tab_control)

    tab_control.add(search_tab, text='Search')
    tab_control.add(reservation_tab, text='Reserve')
    tab_control.pack(expand=1, fill='both')

    # Corrected to match the number of arguments `setup_search_tab` expects
    setup_search_tab(search_tab, role, username)
    search_window.mainloop()

def open_admin_window():
    """Open the admin window."""
    admin_window = tk.Tk()
    admin_window.title("Admin Dashboard")

    tk.Label(admin_window, text="Welcome to Admin Dashboard").pack(pady=20)
    # Add more admin functionalities here
    
    admin_window.mainloop()

# Call the function to open the login window
open_login_window()
