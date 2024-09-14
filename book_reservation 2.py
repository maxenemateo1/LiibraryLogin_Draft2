import tkinter as tk
from tkinter import messagebox, ttk
from database import connect_to_db
from datetime import datetime
from borrowing_books import open_borrowing_books_window  # Import the borrowing window function


# Function definitions from your code
def book_reservation_window(search_tab, reservation_tab, username, role):
    """Set up the search and reserve tab, and the transaction record tab."""
    setup_search_and_reserve_tab(search_tab, username)
    setup_transaction_record_tab(reservation_tab, username)

def setup_search_and_reserve_tab(tab, username):
    """Setup the search and reserve tab with book information, filters, search results, and cart."""
    global book_info_frame, available_label, isbn_label, title_label, author_label, abstract_text, search_tree, cart_tree, add_to_cart_button

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

    # Cart Section
    cart_frame = tk.Frame(content_frame, relief=tk.GROOVE, borderwidth=2)
    cart_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

    tk.Label(cart_frame, text="Cart", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=5)

    # Cart Table
    cart_tree = ttk.Treeview(cart_frame, columns=("title", "isbn"), show="headings", selectmode="extended")
    cart_tree.heading("title", text="Title")
    cart_tree.heading("isbn", text="ISBN")
    cart_tree.pack(side="left", fill=tk.BOTH, expand=1, padx=(10, 0), pady=5)

    # Buttons for Cart
    button_frame = tk.Frame(cart_frame)
    button_frame.pack(side="right", fill=tk.Y, padx=10, pady=10)

    tk.Button(button_frame, text="Remove", relief=tk.GROOVE, command=lambda: remove_from_cart(cart_tree)).pack(side="top", padx=5, pady=5)
    tk.Button(button_frame, text="Reserve", relief=tk.GROOVE, command=lambda: reserve_books(cart_tree, username)).pack(side="top", padx=5, pady=5)
    # New Borrow Books button
    tk.Button(button_frame, text="Borrow Books", relief=tk.GROOVE, command=lambda: open_borrowing_books_window(username)).pack(side="top", padx=5, pady=5)

    # Filter Section
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

# Transaction Tab
def setup_transaction_record_tab(tab, username):
    """Setup the Transaction Record tab with the user's transaction history."""
    content_frame = tk.Frame(tab)
    content_frame.pack(fill=tk.BOTH, expand=1, padx=10, pady=10)

    # Transaction Record Header
    tk.Label(content_frame, text="Transaction Record", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=5)

    # Transaction Table
    transaction_tree = ttk.Treeview(content_frame, columns=("isbn", "date_borrowed", "status"), show="headings", selectmode="browse")
    transaction_tree.heading("isbn", text="ISBN")
    transaction_tree.heading("date_borrowed", text="Date Borrowed")
    transaction_tree.heading("status", text="Status")
    transaction_tree.pack(fill=tk.BOTH, expand=1, padx=10, pady=5)

    # Populate the table with the user's transaction data
    # Replace this with actual database calls to fetch the transaction history for the user
    # Example data for demonstration purposes:
    transaction_data = [
        ("978-3-16-148410-0", "2024-09-01", "Returned"),
        ("978-0-13-110362-7", "2024-09-05", "Borrowed")
    ]
    
    for transaction in transaction_data:
        transaction_tree.insert('', 'end', values=transaction)

    # You can add additional buttons or features here as needed

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
        messagebox.showerror("Database Error", str(e))
    finally:
        conn.close()

def on_search_result_select(event):
    """Handle selection of a search result."""
    selected_item = search_tree.selection()
    if selected_item:
        values = search_tree.item(selected_item[0], "values")
        if values:
            isbn, title = values
            display_book_info(isbn)

def display_book_info(isbn):
    """Fetch and display book information."""
    conn = connect_to_db()
    if conn is None:
        messagebox.showerror("Database Error", "Unable to connect to the database.")
        return

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT ISBN, Title, Author, Abstract FROM tblBooks WHERE ISBN = ?", (isbn,))
        book = cursor.fetchone()
        
        if book:
            isbn_label.config(text=book[0])
            title_label.config(text=book[1])
            author_label.config(text=book[2])
            abstract_text.delete(1.0, tk.END)
            abstract_text.insert(tk.END, book[3])
            available_label.config(text="Yes")  # Example, adjust as needed
        else:
            messagebox.showinfo("No Results", "No book found with that ISBN.")
            clear_book_info()
    except Exception as e:
        messagebox.showerror("Database Error", str(e))
    finally:
        conn.close()

def clear_book_info():
    """Clear the book information fields."""
    isbn_label.config(text="--")
    title_label.config(text="--")
    author_label.config(text="--")
    abstract_text.delete(1.0, tk.END)
    available_label.config(text="--")

def add_to_cart(isbn, title,role):
    """Add selected book to cart."""
    if role == "member":
        cart_tree.insert("", "end", values=(title, isbn))
    else:
        messagebox.showinfo("Cart", "You must be logged in to add books to the cart.")

def remove_from_cart(cart_tree):
    """Remove selected book from cart."""
    selected_item = cart_tree.selection()
    if selected_item:
        cart_tree.delete(selected_item)
    else:
        messagebox.showinfo("Cart", "No book selected to remove.")

def reserve_books(cart_tree, username):
    """Reserve books in the cart for the current member."""
    selected_items = cart_tree.get_children()
    if not selected_items:
        messagebox.showinfo("Cart", "No books selected for reservation.")
        return
    
    conn = connect_to_db()
    if conn is None:
        messagebox.showerror("Database Error", "Unable to connect to the database.")
        return

    cursor = conn.cursor()
    try:
        for item in selected_items:
            values = cart_tree.item(item, "values")
            title, isbn = values
            
            # Create a reservation record
            cursor.execute("INSERT INTO tblReserveTransaction (UserID, ISBN, DateResreved) VALUES (?, ?, ?)",
                           (username, isbn, datetime.now().strftime('%Y-%m-%d')))
        
        conn.commit()
        cart_tree.delete(*cart_tree.get_children())
        messagebox.showinfo("Success", f"You reserved {len(selected_items)} book(s) in your account.")
    except Exception as e:
        messagebox.showerror("Database Error", str(e))
    finally:
        conn.close()

def setup_reservation_tab(tab, username):
    """Setup the reservation tab to display reservation history."""
    reservation_frame = tk.Frame(tab, relief=tk.GROOVE, borderwidth=2)
    reservation_frame.pack(fill=tk.BOTH, expand=1, padx=10, pady=10)

    tk.Label(reservation_frame, text="Reservation History", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=5)

    # Reservation History Table
    reservation_tree = ttk.Treeview(reservation_frame, columns=("isbn", "title", "date_reserved"), show="headings", selectmode="browse")
    reservation_tree.heading("isbn", text="ISBN")
    reservation_tree.heading("title", text="Title")
    reservation_tree.heading("date_reserved", text="Date Reserved")
    reservation_tree.pack(fill=tk.BOTH, expand=1, padx=10, pady=5)

    # Load reservations
    load_reservations(username, reservation_tree)

def load_reservations(username, reservation_tree):
    """Load reservation history for the current member."""
    conn = connect_to_db()
    if conn is None:
        messagebox.showerror("Database Error", "Unable to connect to the database.")
        return

    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT ISBN, Title, DateResreved
            FROM tblReserveTransaction
            JOIN tblBooks ON tblReserveTransaction.ISBN = tblBooks.ISBN
            WHERE UserID = ?
        """, (username,))
        reservations = cursor.fetchall()
        
        # Update the reservation history tree
        reservation_tree.delete(*reservation_tree.get_children())
        for reservation in reservations:
            reservation_tree.insert("", "end", values=reservation)
    except Exception as e:
        messagebox.showerror("Database Error", str(e))
    finally:
        conn.close()

# Main application setup
def main_window():
    """Create the main application window."""
    window = tk.Tk()
    window.title("Library System")
    
    notebook = ttk.Notebook(window)
    notebook.pack(fill=tk.BOTH, expand=1)
    
    # Create tabs for search and reservation
    search_tab = ttk.Frame(notebook)
    reservation_tab = ttk.Frame(notebook)
    
    notebook.add(search_tab, text="Search and Reserve")
    notebook.add(reservation_tab, text="Reservation Record")

    username = "member_user"  # Example username
    role = "member"  # Example role

    # Setup the tabs
    book_reservation_window(search_tab, reservation_tab, username, role)
    
    window.mainloop()

if __name__ == "__main__":
    main_window()
