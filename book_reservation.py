import tkinter as tk
from tkinter import messagebox, ttk
from database import connect_to_db
from datetime import datetime
from book_transaction import setup_borrowing_transaction_facility


def book_reservation_window(search_tab, reservation_tab, username, role):
    """Setup both search and reservation functionalities in the window."""
    setup_search_and_reserve_tab(search_tab, username)
    setup_reservation_tab(reservation_tab, username)

def setup_search_and_reserve_tab(tab, username):
    """Setup the search and reserve tab with book information, filters, search results, and cart."""
    global book_info_frame, available_label, isbn_label, title_label, author_label, abstract_text, search_tree, cart_tree, add_to_cart_button

    # Main content frame
    content_frame = tk.Frame(tab)
    content_frame.pack(fill=tk.BOTH, expand=1, padx=10, pady=10)

    # Book Information Grid: Left Side
    book_info_frame = tk.Frame(content_frame, relief=tk.RIDGE, borderwidth=2)
    book_info_frame.grid(row=0, column=0, sticky="ns", padx=10, pady=10)

    tk.Label(book_info_frame, text="Book Information", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=10, pady=5)

    # Book Details
    tk.Label(book_info_frame, text="Available", anchor="w").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    tk.Label(book_info_frame, text="ISBN", anchor="w").grid(row=2, column=0, padx=10, pady=5, sticky="w")
    tk.Label(book_info_frame, text="Title", anchor="w").grid(row=3, column=0, padx=10, pady=5, sticky="w")
    tk.Label(book_info_frame, text="Author", anchor="w").grid(row=4, column=0, padx=10, pady=5, sticky="w")
    tk.Label(book_info_frame, text="Abstract", anchor="w").grid(row=5, column=0, padx=10, pady=5, sticky="w")

    # Book Information Values
    available_label = tk.Label(book_info_frame, text="--", width=30, relief=tk.SUNKEN)
    isbn_label = tk.Label(book_info_frame, text="--", width=30, relief=tk.SUNKEN)
    title_label = tk.Label(book_info_frame, text="--", width=30, relief=tk.SUNKEN)
    author_label = tk.Label(book_info_frame, text="--", width=30, relief=tk.SUNKEN)
    abstract_text = tk.Text(book_info_frame, height=5, width=30, wrap="word", relief=tk.SUNKEN)

    available_label.grid(row=1, column=1, padx=10, pady=5, sticky="w")
    isbn_label.grid(row=2, column=1, padx=10, pady=5, sticky="w")
    title_label.grid(row=3, column=1, padx=10, pady=5, sticky="w")
    author_label.grid(row=4, column=1, padx=10, pady=5, sticky="w")
    abstract_text.grid(row=5, column=1, padx=10, pady=5, sticky="w")

    # Add 'Add to Cart' button
    add_to_cart_button = tk.Button(book_info_frame, text="Add to Cart", command=lambda: add_to_cart(isbn_label.cget("text"), title_label.cget("text")))
    add_to_cart_button.grid(row=7, column=1, pady=10, sticky="w")

    # Navigation Buttons
    nav_frame = tk.Frame(book_info_frame)
    nav_frame.grid(row=6, column=1, pady=10, sticky="w")

    tk.Button(nav_frame, text="<<", relief=tk.GROOVE, width=3).pack(side="left", padx=5)
    tk.Button(nav_frame, text=">>", relief=tk.GROOVE, width=3).pack(side="left", padx=5)

    # Cart Section (Adjusted to fit buttons to the right of the cart table)
    cart_frame = tk.Frame(content_frame, relief=tk.GROOVE, borderwidth=2)
    cart_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

    tk.Label(cart_frame, text="Cart", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=5)

    # Cart Table
    cart_tree = ttk.Treeview(cart_frame, columns=("title", "isbn"), show="headings", selectmode="extended")
    cart_tree.heading("title", text="Title")
    cart_tree.heading("isbn", text="ISBN")
    cart_tree.pack(side="left", fill=tk.BOTH, expand=1, padx=(10, 0), pady=5)

    # Buttons for Cart (Placed to the right of the cart table)
    button_frame = tk.Frame(cart_frame)
    button_frame.pack(side="right", fill=tk.Y, padx=10, pady=10)

    tk.Button(button_frame, text="Remove", relief=tk.GROOVE, command=lambda: remove_from_cart(cart_tree)).pack(side="top", padx=5, pady=5)
    tk.Button(button_frame, text="Reserve", relief=tk.GROOVE, command=lambda: reserve_books(cart_tree, username)).pack(side="top", padx=5, pady=5)

    # Filter Section: Right Side
    filter_frame = tk.Frame(content_frame, relief=tk.GROOVE, borderwidth=2)
    filter_frame.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)

    tk.Label(filter_frame, text="Filter", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=5)

    # Category Filter
    tk.Label(filter_frame, text="Category").pack(anchor="w", padx=10)
    category_combobox = ttk.Combobox(filter_frame, values=[
        "All", "Communication", "Electronic media", "Mechatronics", "Databases",
        "Electronics Engineering", "Web Design", "Automotive", "Electronics",
        "Plumbing", "Game Art", "Programming", "Utilities", "Networking",
        "Game Design", "Game Programming", "ICT"
    ])
    category_combobox.pack(anchor="w", padx=10, pady=5)

    # Title Filter
    tk.Label(filter_frame, text="Title").pack(anchor="w", padx=10)
    title_entry = tk.Entry(filter_frame)
    title_entry.pack(anchor="w", padx=10, pady=5)

    # ISBN Filter
    tk.Label(filter_frame, text="ISBN").pack(anchor="w", padx=10)
    isbn_entry = tk.Entry(filter_frame)
    isbn_entry.pack(anchor="w", padx=10, pady=5)

    # Search Button
    tk.Button(filter_frame, text="Search", relief=tk.GROOVE, command=lambda: perform_search(title_entry.get(), isbn_entry.get(), category_combobox.get(), search_tree)).pack(pady=10, padx=10)

    # Search Results Section
    search_results_frame = tk.Frame(content_frame, relief=tk.GROOVE, borderwidth=2)
    search_results_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

    tk.Label(search_results_frame, text="Search Results", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=5)

    # Search Results Table
    search_tree = ttk.Treeview(search_results_frame, columns=("isbn", "title"), show="headings", selectmode="browse")
    search_tree.heading("isbn", text="ISBN")
    search_tree.heading("title", text="Title")
    search_tree.pack(fill=tk.BOTH, expand=1, padx=10, pady=5)

    # Bind the selection event to a function
    search_tree.bind("<<TreeviewSelect>>", on_search_result_select)

def perform_search(title, isbn, category, search_tree):
    """Handle search logic and update search results."""
    conn = connect_to_db()
    if conn is None:
        messagebox.showerror("Database Error", "Unable to connect to the database.")
        return

    cursor = conn.cursor()
    query = "SELECT ISBN, Title FROM tblBooks WHERE 1=1"
    parameters = []

    if title:
        query += " AND Title LIKE ?"
        parameters.append(f"%{title}%")
    if isbn:
        query += " AND ISBN = ?"
        parameters.append(isbn)
    if category and category != "All":
        query += " AND Category = ?"
        parameters.append(category)

    try:
        cursor.execute(query, parameters)
        books = cursor.fetchall()
        
        # Update the search results tree
        search_tree.delete(*search_tree.get_children())
        for book in books:
            search_tree.insert("", "end", values=(book[0], book[1]))
    except Exception as e:
        messagebox.showerror("Query Error", f"An error occurred: {e}")
    finally:
        conn.close()

def on_search_result_select(event):
    """Update the book information display when a search result is selected."""
    selected_item = search_tree.selection()
    if not selected_item:
        return

    item = search_tree.item(selected_item[0])
    isbn = item['values'][0]

    conn = connect_to_db()
    if conn is None:
        messagebox.showerror("Database Error", "Unable to connect to the database.")
        return

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT ISBN, Title, Author, Abstract FROM tblBooks WHERE ISBN=?", (isbn,))
        book = cursor.fetchone()
        if book:
            available_label.config(text="Available")
            isbn_label.config(text=book[0])
            title_label.config(text=book[1])
            author_label.config(text=book[2])
            abstract_text.delete(1.0, tk.END)
            abstract_text.insert(tk.END, book[3])
            
            # Show the 'Add to Cart' button
            add_to_cart_button.grid(row=7, column=1, pady=10, sticky="w")
        else:
            messagebox.showwarning("Not Found", "Book details not found.")
    except Exception as e:
        messagebox.showerror("Query Error", f"An error occurred: {e}")
    finally:
        conn.close()

def add_to_cart(isbn, title):
    """Add a book to the cart."""
    if not isbn or not title:
        messagebox.showwarning("Input Error", "ISBN and Title must be provided.")
        return

    # Ensure ISBN is a string
    isbn = str(isbn)

    # Check if the book is already in the cart
    for child in cart_tree.get_children():
        if cart_tree.item(child, 'values') == (title, isbn):
            messagebox.showinfo("Already in Cart", "This book is already in the cart.")
            return

    # Add the book to the cart
    cart_tree.insert("", "end", values=(title, isbn))

def remove_from_cart(cart_tree):
    """Handle removal of selected items from the cart."""
    selected_items = cart_tree.selection()
    if not selected_items:
        messagebox.showwarning("Selection Error", "No item selected. Please select an item to remove.")
        return

    for item in selected_items:
        cart_tree.delete(item)

def reserve_books(cart_tree, username):
    """Handle reservation of books in the cart."""
    if not username:
        messagebox.showwarning("User Error", "Username must be provided.")
        return

    cart_items = cart_tree.get_children()
    if not cart_items:
        messagebox.showwarning("No Items", "No items in the cart to reserve.")
        return

    conn = connect_to_db()
    if conn is None:
        messagebox.showerror("Database Error", "Unable to connect to the database.")
        return

    cursor = conn.cursor()
    try:
        # Retrieve UserID for the given username
        cursor.execute("SELECT UserID FROM tblUsers WHERE Uname = ?", (username,))
        user_id_result = cursor.fetchone()
        if user_id_result is None:
            messagebox.showerror("User Error", "Username not found in the database.")
            return

        user_id = user_id_result[0]

        # Insert each item into tblReserveTransaction
        for item in cart_items:
            isbn = cart_tree.item(item, "values")[1]
            cursor.execute("INSERT INTO tblReserveTransaction (UserID, ISBN, DateReserved) VALUES (?, ?, ?)",
                           (user_id, isbn, datetime.now().date()))
        
        conn.commit()
        messagebox.showinfo("Reservation Successful", "Books have been reserved successfully.")
        cart_tree.delete(*cart_items)

    except Exception as e:
        messagebox.showerror("Reservation Error", f"An error occurred: {e}")
    finally:
        conn.close()


def setup_reservation_tab(tab, username):
    """Setup the reservation tab with a list of current reservations and options to manage them."""
    tk.Label(tab, text="Reservations", font=("Arial", 12, "bold")).pack(pady=20)

    # Reservations Table
    reservation_frame = tk.Frame(tab, relief=tk.GROOVE, borderwidth=2)
    reservation_frame.pack(fill=tk.BOTH, expand=1, padx=10, pady=10)

    tk.Label(reservation_frame, text="Your Reservations", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=5)

    # Reservations Table
    global reservation_tree
    reservation_tree = ttk.Treeview(reservation_frame, columns=("isbn", "title", "date"), show="headings", selectmode="none")
    reservation_tree.heading("isbn", text="ISBN")
    reservation_tree.heading("title", text="Title")
    reservation_tree.heading("date", text="Reservation Date")
    reservation_tree.pack(fill=tk.BOTH, expand=1, padx=10, pady=5)

    # Load reservations
    load_reservations(username)

def load_reservations(username):
    """Load reservations for the given username and populate the reservations table."""
    conn = connect_to_db()
    if conn is None:
        messagebox.showerror("Database Error", "Unable to connect to the database.")
        return

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT ISBN, DateResreved FROM tblReserveTransaction WHERE UserID=?", (username,))
        reservations = cursor.fetchall()
        
        # Update the reservations tree
        reservation_tree.delete(*reservation_tree.get_children())
        for reservation in reservations:
            reservation_tree.insert("", "end", values=(reservation[0], reservation[1], reservation[2]))
    except Exception as e:
        messagebox.showerror("Query Error", f"An error occurred: {e}")
    finally:
        conn.close()

# Example Tkinter setup
root = tk.Tk()
search_tab = tk.Frame(root)
reservation_tab = tk.Frame(root)
root.mainloop()
