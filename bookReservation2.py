import tkinter as tk 
from tkinter import messagebox, ttk
from database import connect_to_db
from datetime import datetime

# Book Reservation Window
def setup_borrowing_tab(tab, username):
    """Setup the borrowing tab with a list of borrowed books and return functionality."""
    tk.Label(tab, text="Borrowed Books", font=("Arial", 12, "bold")).pack(pady=20)

    # Borrowed Books Table
    global borrowing_tree
    borrowing_frame = tk.Frame(tab, relief=tk.GROOVE, borderwidth=2)
    borrowing_frame.pack(fill=tk.BOTH, expand=1, padx=10, pady=10)

    tk.Label(borrowing_frame, text="Your Borrowed Books", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=5)

    borrowing_tree = ttk.Treeview(borrowing_frame, columns=("isbn", "title", "date"), show="headings", selectmode="extended")
    borrowing_tree.heading("isbn", text="ISBN")
    borrowing_tree.heading("title", text="Title")
    borrowing_tree.heading("date", text="Date Borrowed")
    borrowing_tree.pack(fill=tk.BOTH, expand=1, padx=10, pady=5)

    # Buttons for Borrowing Tab
    button_frame = tk.Frame(borrowing_frame)
    button_frame.pack(fill=tk.X, padx=10, pady=5)

    tk.Button(button_frame, text="Return Selected Book", command=lambda: return_book(username)).pack(side="left", padx=5)
    tk.Button(button_frame, text="Borrow Reserved Books", command=lambda: borrow_reserved_books(username)).pack(side="left", padx=5)

    # Load borrowed books for the user
    load_borrowed_books(username)

    # Setup Borrowing Tab
def setup_borrowing_tab(tab, username):
    """Setup the borrowing tab with a list of borrowed books and return functionality."""
    tk.Label(tab, text="Borrowed Books", font=("Arial", 12, "bold")).pack(pady=20)

    # Borrowed Books Table
    global borrowing_tree
    borrowing_frame = tk.Frame(tab, relief=tk.GROOVE, borderwidth=2)
    borrowing_frame.pack(fill=tk.BOTH, expand=1, padx=10, pady=10)

    tk.Label(borrowing_frame, text="Your Borrowed Books", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=5)

    borrowing_tree = ttk.Treeview(borrowing_frame, columns=("isbn", "title", "date"), show="headings", selectmode="extended")
    borrowing_tree.heading("isbn", text="ISBN")
    borrowing_tree.heading("title", text="Title")
    borrowing_tree.heading("date", text="Date Borrowed")
    borrowing_tree.pack(fill=tk.BOTH, expand=1, padx=10, pady=5)

    # Buttons for Borrowing Tab
    button_frame = tk.Frame(borrowing_frame)
    button_frame.pack(fill=tk.X, padx=10, pady=5)

    tk.Button(button_frame, text="Return Selected Book", command=lambda: return_book(username)).pack(side="left", padx=5)
    tk.Button(button_frame, text="Borrow Reserved Books", command=lambda: borrow_reserved_books(username)).pack(side="left", padx=5)

    # Load borrowed books for the user
    load_borrowed_books(username)

# Load Borrowed Books
def load_borrowed_books(username):
    """Load borrowed books for the given username and populate the borrowing transactions table."""
    conn = connect_to_db()
    if conn is None:
        messagebox.showerror("Database Error", "Unable to connect to the database.")
        return

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT UserID FROM tblusers WHERE Username=?", (username,))
        user_id = cursor.fetchone()[0]

        cursor.execute("""
            SELECT tblBorrowTran.ISBN, tblBooks.Title, tblBorrowTran.DateBorrowed
            FROM tblBorrowTran
            INNER JOIN tblBooks ON tblBorrowTran.ISBN = tblBooks.ISBN
            WHERE tblBorrowTran.UserID=?
              AND tblBorrowTran.IsBookReturned=0
            """, (user_id,))
        borrowed_books = cursor.fetchall()

        borrowing_tree.delete(*borrowing_tree.get_children())
        for book in borrowed_books:
            borrowing_tree.insert("", "end", values=(book[0], book[1], book[2]))
    except Exception as e:
        messagebox.showerror("Query Error", f"An error occurred: {e}")
    finally:
        conn.close()

# Borrow Books
def borrow_book(isbn, username):
    """Handle borrowing a book."""
    conn = connect_to_db()
    if conn is None:
        messagebox.showerror("Database Error", "Unable to connect to the database.")
        return

    cursor = conn.cursor()
    try:
        # Check if the book is available
        cursor.execute("SELECT InStock FROM tblBooks WHERE ISBN = ?", (isbn,))
        book = cursor.fetchone()
        if not book or book[0] <= 0:
            messagebox.showwarning("Book Unavailable", "The book is not available for borrowing.")
            conn.close()
            return

        # Insert a new borrowing transaction
        cursor.execute("INSERT INTO tblBorrowTran (UserID, ISBN, DateBorrowed) VALUES ((SELECT UserID FROM Users WHERE Username = ?), ?, ?)",
                       (username, isbn, datetime.now()))

        # Update the book stock
        cursor.execute("UPDATE tblBooks SET InStock = InStock - 1 WHERE ISBN = ?", (isbn,))

        conn.commit()
        messagebox.showinfo("Borrow Successful", "The book has been borrowed successfully.")

    except Exception as e:
        messagebox.showerror("Database Error", f"Error executing query: {e}")

    conn.close()
    load_borrowing_records(username)

# Loadd Borrowing Records
def load_borrowing_records(username, borrow_tree):
    """Load borrowing records for the user and update the borrow tree."""
    conn = connect_to_db()
    if conn is None:
        messagebox.showerror("Database Error", "Unable to connect to the database.")
        return

    cursor = conn.cursor()
    query = """SELECT bt.ISBN, b.Title, bt.DateBorrowed, bt.IsBookReturned
               FROM tblBorrowTran bt
               JOIN tblBooks b ON bt.ISBN = b.ISBN
               JOIN Users u ON bt.UserID = u.UserID
               WHERE u.Username = ?"""
    
    try:
        cursor.execute(query, (username,))
        borrowings = cursor.fetchall()
    except Exception as e:
        messagebox.showerror("Database Error", f"Error executing query: {e}")
        conn.close()
        return

    # Clear previous records in the borrow tree
    for row in borrow_tree.get_children():
        borrow_tree.delete(row)

    # Insert new records into the borrow tree
    for borrowing in borrowings:
        borrow_tree.insert("", "end", values=(borrowing[0], borrowing[1], borrowing[2], "Yes" if borrowing[3] else "No"))

    conn.close()


def setup_search_and_reserve_tab(tab, username):
    """Setup the search and reserve tab with book information, filters, search results, and cart."""
    global book_info_frame, available_label, isbn_label, title_label, author_label, abstract_text
    global search_tree, cart_tree, add_to_cart_button, category_combobox, title_entry, isbn_entry

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
    except Exception as e:
        messagebox.showerror("Database Error", f"Error executing query: {e}")
        conn.close()
        return

    # Clear previous results
    for row in search_tree.get_children():
        search_tree.delete(row)

    # Insert new results
    for book in books:
        search_tree.insert("", "end", values=(book[0], book[1]))

    conn.close()


def on_search_result_select(event):
    """Handle book selection from search results."""
    selected_item = search_tree.selection()
    if not selected_item:
        return

    item = search_tree.item(selected_item)
    isbn = item['values'][0]
    # Populate book information
    load_book_info(isbn)

def load_book_info(isbn):
    """Load detailed book information based on selected ISBN."""
    conn = connect_to_db()
    if conn is None:
        messagebox.showerror("Database Error", "Unable to connect to the database.")
        return

    cursor = conn.cursor()
    query = "SELECT ISBN, Title, Author, Abstract, InStock FROM tblBooks WHERE tblBooks.ISBN = ?"
    
    try:
        cursor.execute(query, (isbn,))
        book = cursor.fetchone()
    except Exception as e:
        messagebox.showerror("Database Error", f"Error executing query: {e}")
        conn.close()
        return

    if book:
        isbn_label.config(text=book[0])
        title_label.config(text=book[1])
        author_label.config(text=book[2])
        abstract_text.delete(1.0, tk.END)
        abstract_text.insert(tk.END, book[3])
        available_label.config(text="Yes" if book[4] > 0 else "No")
    else:
        messagebox.showwarning("No Results", "No book details found.")

    conn.close()

# Add to Cart
def add_to_cart(isbn, title):
    """Add selected book to cart."""
    if isbn == "--":
        messagebox.showwarning("No Selection", "No book selected to add to cart.")
        return

    for item in cart_tree.get_children():
        if cart_tree.item(item, "values")[1] == isbn:
            messagebox.showinfo("Already in Cart", "This book is already in your cart.")
            return

    cart_tree.insert("", "end", values=(title, isbn))

def remove_from_cart(cart_tree):
    """Remove selected book from the cart."""
    selected_item = cart_tree.selection()
    if not selected_item:
        messagebox.showwarning("No Selection", "No book selected to remove from cart.")
        return

    for item in selected_item:
        cart_tree.delete(item)

def reserve_books(cart_tree, username):
    """Reserve books in the cart for the user."""
    conn = connect_to_db()
    if conn is None:
        messagebox.showerror("Database Error", "Unable to connect to the database.")
        return

    cursor = conn.cursor()
    reserved_count = 0
    for item in cart_tree.get_children():
        isbn = cart_tree.item(item, "values")[1]
        try:
            cursor.execute("INSERT INTO tblReserveTransaction (UserID, ISBN, DateResreved) VALUES ((SELECT UserID FROM Users WHERE Username = ?), ?, ?)",
                           (username, isbn, datetime.now()))
            reserved_count += 1
        except Exception as e:
            messagebox.showerror("Database Error", f"Error executing query: {e}")

    conn.commit()
    conn.close()

    if reserved_count > 0:
        messagebox.showinfo("Reservation Successful", f"You reserved {reserved_count} book(s) in your account.")
    else:
        messagebox.showwarning("No Books Reserved", "No books were reserved. Please try again.")

# Setup reservation Tab
def setup_reservation_tab(tab, username):
    """Setup the reservation tab with a list of current reservations and options to manage them."""
    tk.Label(tab, text="Reservations", font=("Arial", 12, "bold")).pack(pady=20)

    # Reservations Table
    global reserved_tree
    reservation_frame = tk.Frame(tab, relief=tk.GROOVE, borderwidth=2)
    reservation_frame.pack(fill=tk.BOTH, expand=1, padx=10, pady=10)

    tk.Label(reservation_frame, text="Your Reservations", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=5)

    reserved_tree = ttk.Treeview(reservation_frame, columns=("isbn", "title"), show="headings", selectmode="extended")
    reserved_tree.heading("isbn", text="ISBN")
    reserved_tree.heading("title", text="Title")
    reserved_tree.pack(fill=tk.BOTH, expand=1, padx=10, pady=5)

    # Load reservations
    load_reserved_books(username)

    # Loadd Reserved Books
def load_reserved_books(username):
    """Load reserved books for the given username and populate the reservations table."""
    conn = connect_to_db()
    if conn is None:
        messagebox.showerror("Database Error", "Unable to connect to the database.")
        return

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT UserID FROM tblusers WHERE Username=?", (username,))
        user_id = cursor.fetchone()[0]

        cursor.execute("""
            SELECT tblReserveTransaction.ISBN, tblBooks.Title
            FROM tblReserveTransaction
            INNER JOIN tblBooks ON tblReserveTransaction.ISBN = tblBooks.ISBN
            WHERE tblReserveTransaction.UserID=?
              AND tblReserveTransaction.IsBookBorrowed=0
            """, (user_id,))
        reserved_books = cursor.fetchall()

        reserved_tree.delete(*reserved_tree.get_children())
        for book in reserved_books:
            reserved_tree.insert("", "end", values=(book[0], book[1]))
    except Exception as e:
        messagebox.showerror("Query Error", f"An error occurred: {e}")
    finally:
        conn.close()

def load_reservation_records(username, reservation_tree):
    """Load reservation records for the user and update the reservation tree."""
    conn = connect_to_db()
    if conn is None:
        messagebox.showerror("Database Error", "Unable to connect to the database.")
        return

    cursor = conn.cursor()
    query = """SELECT rt.ISBN, b.Title, rt.DateReserved
               FROM tblReserveTransaction rt
               JOIN tblBooks b ON rt.ISBN = b.ISBN
               JOIN Users u ON rt.UserID = u.UserID
               WHERE u.Username = ?"""
    
    try:
        cursor.execute(query, (username,))
        reservations = cursor.fetchall()
    except Exception as e:
        messagebox.showerror("Database Error", f"Error executing query: {e}")
        conn.close()
        return

    # Clear previous records in the reservation tree
    for row in reservation_tree.get_children():
        reservation_tree.delete(row)

    # Insert new records into the reservation tree
    for reservation in reservations:
        reservation_tree.insert("", "end", values=(reservation[0], reservation[1], reservation[2]))

    conn.close()


# Return Book
def return_book(username):
    """Handle the return of selected books."""
    selected_items = borrowing_tree.selection()
    if not selected_items:
        messagebox.showwarning("Selection Error", "No book selected. Please select a book to return.")
        return

    conn = connect_to_db()
    if conn is None:
        messagebox.showerror("Database Error", "Unable to connect to the database.")
        return

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT UserID FROM tblusers WHERE Username=?", (username,))
        user_id = cursor.fetchone()[0]

        for item in selected_items:
            isbn = borrowing_tree.item(item, "values")[0]

            cursor.execute("""
                UPDATE tblBorrowTran
                SET IsBookReturned=1
                WHERE UserID=? AND ISBN=? AND IsBookReturned=0
                """, (user_id, isbn))

            cursor.execute("""
                INSERT INTO tblReturnTransaction (UserID, BTransactionNo, ISBN, DateReturned, Status)
                SELECT UserID, TransactionNo, ISBN, ?, 'Returned'
                FROM tblBorrowTran
                WHERE UserID=? AND ISBN=? AND IsBookReturned=0
                """, (datetime.now().date(), user_id, isbn))

        conn.commit()
        messagebox.showinfo("Return Successful", "Selected books have been returned successfully.")
        load_borrowed_books(username)  # Refresh the list
    except Exception as e:
        messagebox.showerror("Return Error", f"An error occurred: {e}")
    finally:
        conn.close()

# Borrow Reserved Books
def borrow_reserved_books(username):
    """Handle the borrowing of reserved books."""
    selected_items = reserved_tree.selection()
    if not selected_items:
        messagebox.showwarning("Selection Error", "No reserved book selected. Please select a book to borrow.")
        return

    conn = connect_to_db()
    if conn is None:
        messagebox.showerror("Database Error", "Unable to connect to the database.")
        return

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT UserID FROM tblusers WHERE Username=?", (username,))
        user_id = cursor.fetchone()[0]

        for item in selected_items:
            isbn = reserved_tree.item(item, "values")[0]

            cursor.execute("""
                UPDATE tblReserveTransaction
                SET IsBookBorrowed=1
                WHERE UserID=? AND ISBN=? AND IsBookBorrowed=0
                """, (user_id, isbn))

            cursor.execute("""
                INSERT INTO tblBorrowTran (UserID, ISBN, DateBorrowed, IsBookReturned)
                VALUES (?, ?, ?, 0)
                """, (user_id, isbn, datetime.now().date()))

        conn.commit()
        messagebox.showinfo("Borrowing Successful", "Selected reserved books have been borrowed successfully.")
        load_reserved_books(username)  # Refresh the list
        load_borrowed_books(username)  # Refresh the borrowed books list
    except Exception as e:
        messagebox.showerror("Borrow Error", f"An error occurred: {e}")
    finally:
        conn.close()

# Example Tkinter setup
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Library System")
    tab_control = ttk.Notebook(root)

    borrowing_tab = tk.Frame(tab_control)
    reservation_tab = tk.Frame(tab_control)

    tab_control.add(borrowing_tab, text="Borrowing")
    tab_control.add(reservation_tab, text="Reservations")
    tab_control.pack(expand=1, fill="both")

    # Replace 'username' with the actual username you want to use
    setup_borrowing_tab(borrowing_tab, 'username')
    setup_reservation_tab(reservation_tab, 'username')

    root.mainloop()
