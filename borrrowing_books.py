import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime, timedelta
from database import connect_to_db  # Import the get_connection function

def open_borrowing_books_window(username):
    """Open a new window for managing borrowing books."""
    window = tk.Toplevel()  # Create a new top-level window
    window.title("Borrowing Books Management")
    
    setup_borrowing_books_tab(window, username)

def setup_borrowing_books_tab(tab, username):
    """Setup the borrowing books tab with transaction management and reservation records."""
    global search_results_tree, member_id_entry, transaction_tree

    content_frame = tk.Frame(tab)
    content_frame.pack(fill=tk.BOTH, expand=1, padx=10, pady=10)

    # Header
    header_frame = tk.Frame(content_frame)
    header_frame.pack(fill=tk.X, pady=(0, 10))

    tk.Label(header_frame, text="ABC Learning Resource Center", font=("Arial", 16, "bold")).pack(side="left", padx=10)
    tk.Label(header_frame, text=f"Welcome, {username}!", font=("Arial", 12)).pack(side="right", padx=10)

    # Main Tab Control
    tab_control = ttk.Notebook(content_frame)
    tab_control.pack(fill=tk.BOTH, expand=1)

    # Borrow Transactions Tab
    borrow_tab = tk.Frame(tab_control)
    tab_control.add(borrow_tab, text="Borrow Transactions")

    # Nested Tab Control inside "Borrow Transactions"
    nested_tab_control = ttk.Notebook(borrow_tab)
    nested_tab_control.pack(fill=tk.BOTH, expand=1, padx=10, pady=10)

    # Manual Entry Tab (inside Borrow Transactions)
    manual_entry_tab = tk.Frame(nested_tab_control)
    nested_tab_control.add(manual_entry_tab, text="Manual Entry")

    # Reservation Tab (inside Borrow Transactions)
    reservation_tab_inner = tk.Frame(nested_tab_control)
    nested_tab_control.add(reservation_tab_inner, text="Reservation")

    # Add content for Manual Entry Tab
    setup_manual_entry_tab(manual_entry_tab)

    # Add content for Reservation Tab (inside Borrow Transactions)
    setup_inner_reservation_tab(reservation_tab_inner)

    # Reservation Tab (Main Tab Control)
    reservation_tab = tk.Frame(tab_control)
    tab_control.add(reservation_tab, text="Return Transactions")

    # Log Out Button
    logout_button = tk.Button(content_frame, text="Log Out", command=logout)
    logout_button.pack(side="right", padx=10, pady=10)
    
def submit_borrow_request(member_id, isbn):
    """Submit the borrow request form."""
    if not member_id or not isbn:
        messagebox.showwarning("Warning", "Please fill in all fields.")
        return

    conn = connect_to_db()
    cursor = conn.cursor()

    # Insert the borrow transaction into the database
    date_borrowed = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("INSERT INTO tblBorrowTran (UserID, ISBN, DateBorrowed) VALUES (?, ?, ?)",
                   (member_id, isbn, date_borrowed))

    conn.commit()
    conn.close()

    messagebox.showinfo("Success", f"Borrow request for ISBN {isbn} submitted.")

def setup_manual_entry_tab(tab):
def setup_manual_entry_tab(tab, username):
    """Setup the Manual Entry sub-tab with book information, filters, and cart."""
    global book_info_frame, search_tree, cart_tree

    content_frame = tk.Frame(tab)
    content_frame.pack(fill=tk.BOTH, expand=1, padx=10, pady=10)

    # Book Information Grid
    book_info_frame = tk.Frame(content_frame, relief=tk.RIDGE, borderwidth=2)
    book_info_frame.grid(row=0, column=0, sticky="ns", padx=10, pady=10)

    tk.Label(book_info_frame, text="Book Information", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=10, pady=5)

    tk.Label(book_info_frame, text="Available", anchor="w").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    tk.Label(book_info_frame, text="ISBN", anchor="w").grid(row=2, column=0, padx=10, pady=5, sticky="w")
    tk.Label(book_info_frame, text="Title", anchor="w").grid(row=3, column=0, padx=10, pady=5, sticky="w")
    tk.Label(book_info_frame, text="Author", anchor="w").grid(row=4, column=0, padx=10, pady=5, sticky="w")
    tk.Label(book_info_frame, text="Abstract", anchor="w").grid(row=5, column=0, padx=10, pady=5, sticky="w")

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
    category_combobox.set("All")
    category_combobox.pack(fill=tk.X, padx=10, pady=5)

    # Title Filter
    tk.Label(filter_frame, text="Title").pack(anchor="w", padx=10)
    title_entry = tk.Entry(filter_frame)
    title_entry.pack(fill=tk.X, padx=10, pady=5)

    # Author Filter
    tk.Label(filter_frame, text="Author").pack(anchor="w", padx=10)
    author_entry = tk.Entry(filter_frame)
    author_entry.pack(fill=tk.X, padx=10, pady=5)

    # ISBN Filter
    tk.Label(filter_frame, text="ISBN").pack(anchor="w", padx=10)
    isbn_entry = tk.Entry(filter_frame)
    isbn_entry.pack(fill=tk.X, padx=10, pady=5)

    # Search Button
    search_button = tk.Button(filter_frame, text="Search", command=lambda: perform_search_transaction(
        category_combobox.get(), title_entry.get(), author_entry.get(), isbn_entry.get(), search_tree))
    search_button.pack(padx=10, pady=10)    

def perform_search(member_id, search_tree):
    """Perform the search based on member ID and update search_tree."""
    # Placeholder implementation; replace with actual database query and result population
    search_tree.delete(*search_tree.get_children())  # Clear existing results

    # Mockup data for demonstration purposes
    mock_data = [
        ("001", "0324785151", "2024-09-01"),
        ("002", "0324785161", "2024-09-05")
    ]

    for record in mock_data:
        search_tree.insert("", tk.END, values=record)



def setup_search_transaction_record_tab(tab, username):
    """Setup the Search Transaction Record sub-tab with search functionality and transaction results."""
    global search_tree

    content_frame = tk.Frame(tab)
    content_frame.pack(fill=tk.BOTH, expand=1, padx=10, pady=10)

    # Search Panel
    search_panel = tk.Frame(content_frame, relief=tk.GROOVE, borderwidth=2)
    search_panel.pack(fill=tk.X, padx=10, pady=10)

    tk.Label(search_panel, text="Enter Member's ID No:").pack(side=tk.LEFT, padx=10, pady=5)
    member_id_entry = tk.Entry(search_panel)
    member_id_entry.pack(side=tk.LEFT, padx=10, pady=5)

    search_button = tk.Button(search_panel, text="Search", command=lambda: perform_search(member_id_entry.get(), search_tree))
    search_button.pack(side=tk.LEFT, padx=10, pady=5)

    # Search Results Section
    search_results_frame = tk.Frame(content_frame, relief=tk.GROOVE, borderwidth=2)
    search_results_frame.pack(fill=tk.BOTH, expand=1, padx=10, pady=10)

    tk.Label(search_results_frame, text="Search Results", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=5)

    # Search Results Table
    search_tree = ttk.Treeview(search_results_frame, columns=("transaction_no", "isbn", "date_borrowed"), show="headings", selectmode="browse")
    search_tree.heading("transaction_no", text="Transaction No")
    search_tree.heading("isbn", text="ISBN")
    search_tree.heading("date_borrowed", text="Date Borrowed")
    search_tree.pack(fill=tk.BOTH, expand=1, padx=10, pady=5)

    # Bind the selection event to a function
    search_tree.bind("<<TreeviewSelect>>", on_transaction_select)

    # Buttons for Cart
    button_frame = tk.Frame(content_frame)
    button_frame.pack(fill=tk.X, padx=10, pady=10)

    tk.Button(button_frame, text="Remove Selected Item", command=lambda: remove_selected_item(search_tree)).pack(side=tk.LEFT, padx=10, pady=5)
    tk.Button(button_frame, text="Lend Listed Books", command=lambda: lend_listed_books(search_tree, username)).pack(side=tk.LEFT, padx=10, pady=5)


def search_books(tree, category, title, author, isbn):
    """Search for books based on filter criteria and update the book_info_tree."""
    conn = connect_to_db()
    cursor = conn.cursor()

    query = '''
    SELECT ISBN, Title, Author, Description FROM tblBooks
    WHERE (Category = ? OR ? = '') 
      AND (Title LIKE ? OR ? = '') 
      AND (Author LIKE ? OR ? = '') 
      AND (ISBN LIKE ? OR ? = '')
    '''
    cursor.execute(query, (category, category, f"%{title}%", title, f"%{author}%", author, f"%{isbn}%", isbn))
    books = cursor.fetchall()

    tree.delete(*tree.get_children())

    for book in books:
        tree.insert("", tk.END, values=book)

    conn.close()

def on_search_result_select(event):
    """Handle the selection of a book from the search results."""
    # Get the selected item
    selected_item = search_tree.selection()

    if selected_item:
        # Get the data for the selected item
        selected_book = search_tree.item(selected_item[0], 'values')
        if selected_book:
            isbn = selected_book[0]
            title = selected_book[1]

            # Retrieve book details from the database
            book_details = get_book_details(isbn)
            
            # Update the book information display
            if book_details:
                available_label.config(text=book_details['Available'])
                isbn_label.config(text=book_details['ISBN'])
                title_label.config(text=book_details['Title'])
                author_label.config(text=book_details['Author'])
                abstract_text.delete(1.0, tk.END)
                abstract_text.insert(tk.END, book_details['Abstract'])

def get_book_details(isbn):
    """Fetch book details from the database based on the ISBN."""
    # Replace with actual database query logic
    # This is a mockup for demonstration purposes
    # Simulating a book detail dictionary as an example
    example_books = {
        '0324785151': {
            'Available': 'Yes',
            'ISBN': '0324785151',
            'Title': 'Example Book Title',
            'Author': 'Example Author',
            'Abstract': 'This is an example abstract of the book.'
        }
        # Add other example books here
    }
    return example_books.get(isbn, None)               
def add_to_cart(book_info_tree, cart_tree):
    """Add selected books from book_info_tree to cart_tree."""
    selected_items = book_info_tree.selection()
    for item in selected_items:
        values = book_info_tree.item(item, "values")
        if values not in [cart_tree.item(child, "values") for child in cart_tree.get_children()]:
            cart_tree.insert("", tk.END, values=values)

def open_member_id_confirmation_dialog():
    """Open a dialog to confirm Member's ID before proceeding with borrowing."""
    confirmation_dialog = tk.Toplevel()
    confirmation_dialog.title("Confirm Member's ID")

    tk.Label(confirmation_dialog, text="Enter Member's ID No:").pack(padx=10, pady=5)

    member_id_entry = tk.Entry(confirmation_dialog)
    member_id_entry.pack(padx=10, pady=5)

    button_frame = tk.Frame(confirmation_dialog)
    button_frame.pack(pady=10)

    continue_button = tk.Button(button_frame, text="Continue", command=lambda: confirm_member_id(member_id_entry.get(), confirmation_dialog))
    continue_button.pack(side="left", padx=5)

    cancel_button = tk.Button(button_frame, text="Cancel", command=confirmation_dialog.destroy)
    cancel_button.pack(side="left", padx=5)
    cancel_button.pack(side="left", padx=5)

def confirm_member_id(member_id, dialog):
    """Confirm Member's ID and process cart items."""
    if not member_id:
        messagebox.showwarning("Input Error", "Please enter a valid Member ID.")
        return

    # Add your logic to handle the borrowing process
    # For example, processing the cart items and updating the database

    messagebox.showinfo("Success", "Borrowing processed successfully.")

    # Close the confirmation dialog
    dialog.destroy()

def setup_inner_reservation_tab(reservation_tab_inner):
    """Setup content for the Reservation tab inside Borrow Transactions."""
    reservation_frame_inner = tk.Frame(reservation_tab_inner)
    reservation_frame_inner.pack(fill=tk.BOTH, expand=1, padx=10, pady=10)

    tk.Label(reservation_frame_inner, text="Borrow Reservation Records", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=5)

    # Search Member's ID Section
    search_frame = tk.Frame(reservation_frame_inner)
    search_frame.pack(fill=tk.X, padx=10, pady=5)

    tk.Label(search_frame, text="Enter Member's ID No:").pack(side="left", padx=5)
    member_id_entry = tk.Entry(search_frame)
    member_id_entry.pack(side="left", padx=5)

    search_button = tk.Button(search_frame, text="Search", command=search_transaction_records)
    search_button.pack(side="left", padx=5)

    # Transaction Table
    transaction_frame = tk.Frame(reservation_frame_inner)
    transaction_frame.pack(fill=tk.BOTH, expand=1, padx=10, pady=10)

    transaction_tree = ttk.Treeview(transaction_frame, columns=("isbn", "title", "member_id", "transaction_no"), show="headings")
    transaction_tree.heading("isbn", text="ISBN")
    transaction_tree.heading("title", text="Title")
    transaction_tree.heading("member_id", text="Member ID")
    transaction_tree.heading("transaction_no", text="Transaction No")
    transaction_tree.pack(fill=tk.BOTH, expand=1)

    # Add Scrollbar to Transaction Table
    scrollbar = ttk.Scrollbar(transaction_frame, orient="vertical", command=transaction_tree.yview)
    transaction_tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # Buttons for actions
    action_frame = tk.Frame(reservation_frame_inner)
    action_frame.pack(fill=tk.X, pady=10)

    remove_button = tk.Button(action_frame, text="Remove Selected Item", command=lambda: remove_selected_item(transaction_tree))
    remove_button.pack(side="left", padx=5)

    lend_button = tk.Button(action_frame, text="Lend Listed Books", command=lambda: lend_books(transaction_tree))
    lend_button.pack(side="left", padx=5)

def search_reservation(member_id):
    """Function to search for reserved books by member ID and update search_results_tree."""
    conn = connect_to_db()
    cursor = conn.cursor()

    query = '''
    SELECT tblBooks.ISBN, tblBooks.Title FROM tblReserveTransaction
    JOIN tblBooks ON tblReserveTransaction.ISBN = tblBooks.ISBN
    WHERE tblReserveTransaction.UserID = ?
    '''
    cursor.execute(query, (member_id,))
    reserved_books = cursor.fetchall()

    search_results_tree.delete(*search_results_tree.get_children())

    for book in reserved_books:
        search_results_tree.insert("", tk.END, values=book)

    conn.close()

def remove_selected_book():
    """Function to remove selected reserved books."""
    selected_items = search_results_tree.selection()
    conn = connect_to_db()
    cursor = conn.cursor()

    for item in selected_items:
        isbn = search_results_tree.item(item, "values")[0]
        cursor.execute("DELETE FROM tblReserveTransaction WHERE ISBN = ?", (isbn,))
        search_results_tree.delete(item)

    conn.commit()
    conn.close()
    messagebox.showinfo("Info", "Selected books removed successfully.")

def transfer_to_borrow():
    """Function to transfer selected reserved books to borrow records."""
    selected_items = search_results_tree.selection()
    if not selected_items:
        messagebox.showwarning("Warning", "No books selected for transfer.")
        return

    conn = connect_to_db()
    cursor = conn.cursor()

    member_id = member_id_entry.get()

    for item in selected_items:
        isbn = search_results_tree.item(item, "values")[0]
        cursor.execute("INSERT INTO tblBorrowTran (UserID, ISBN, DateBorrowed) VALUES (?, ?, ?)",
                       (member_id, isbn, datetime.now().strftime("%Y-%m-%d")))
        cursor.execute("DELETE FROM tblReserveTransaction WHERE ISBN = ?", (isbn,))

    conn.commit()
    conn.close()

    generate_report()

def transfer_reserved_books():
    """Function to handle book transfer from reservation to borrow records."""
    # Placeholder for additional functionality if needed
    pass

def generate_report():
    """Function to generate a printable report for the transaction."""
    date_borrowed = datetime.now().strftime("%Y-%m-%d")
    due_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
    transaction_number = "TXN12345"  # Generate or fetch transaction number
    member_name = "John Doe"  # Replace with actual member name
    member_id = member_id_entry.get()

    report_text = (
        f"Date Borrowed: {date_borrowed}\n"
        f"Due Date: {due_date}\n"
        f"Transaction Number: {transaction_number}\n"
        f"List of Books Borrowed:\n"
    )

    for item in transaction_tree.get_children():
        values = transaction_tree.item(item, "values")
        report_text += f"Title: {values[1]}, ISBN: {values[0]}\n"

    report_text += (
        f"\nName of Member: {member_name}\n"
        f"Member's ID Number: {member_id}\n"
    )

    messagebox.showinfo("Transaction Report", report_text)

def add_manual_entry(isbn, title, author):
    """Function to handle adding manual book entries."""
    # Logic to add the book to the system
    messagebox.showinfo("Info", f"Book added: {title} (ISBN: {isbn})")

def remove_selected_item(tree):
    """Remove the selected item from the transaction list."""
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Selection Error", "Please select an item to remove.")
        return

    for item in selected_item:
        tree.delete(item)
    messagebox.showinfo("Success", "Selected item removed.")

def search_transaction_records():
    """Search for transaction records based on the entered Member ID."""
    member_id = member_id_entry.get()
    if not member_id:
        messagebox.showwarning("Input Error", "Please enter a valid Member ID.")
        return

    # Add logic to search and populate the transaction_tree with the member's transactions
    # Example (Replace with your database logic):
    # for each record in database search result:
    #     transaction_tree.insert('', 'end', values=(isbn, title, member_id, transaction_no))

    # Simulated example (replace this with actual data retrieval):
    transaction_tree.insert('', 'end', values=("978-0324785151", "Database Management", member_id, "TRX-001"))
    transaction_tree.insert('', 'end', values=("978-0135166307", "Introduction to Python", member_id, "TRX-002"))

def lend_books(tree):
    """Mark listed books as lent to the member."""
    selected_items = tree.get_children()
    if not selected_items:
        messagebox.showwarning("Error", "There are no items to lend.")
        return

    # Logic to mark the listed books as lent in the database for the current member.
    # Example:
    # for item in selected_items:
    #     values = tree.item(item, "values")
    #     isbn, title, member_id, transaction_no = values
    #     # Process lending in the system, update DB, etc.

    messagebox.showinfo("Success", "Listed books have been lent to the member.")
    # Optionally clear the tree after lending
    tree.delete(*selected_items)

def logout():
    """Function to handle logging out."""
    # Implement the logic to handle user logout
    pass
