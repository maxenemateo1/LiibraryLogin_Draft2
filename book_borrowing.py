import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime, timedelta
from database import connect_to_db

def open_borrowing_window():
    """Open the Borrowing Transaction window."""
    borrowing_window = tk.Toplevel()
    borrowing_window.title("Borrowing Transactions")
    borrowing_window.geometry("1200x600")  # Adjust size as needed

    # Create tabs for Borrowing Transaction and Reservation Management
    tab_control = ttk.Notebook(borrowing_window)
    borrow_transaction_tab = ttk.Frame(tab_control)
    reservation_tab = ttk.Frame(tab_control)

    tab_control.add(borrow_transaction_tab, text='Borrow Transaction')
    tab_control.add(reservation_tab, text='From Reservation')
    tab_control.pack(expand=1, fill='both')

    # Set up both tabs
    setup_borrow_transaction_tab(borrow_transaction_tab)
    setup_reservation_tab(reservation_tab)

def setup_borrow_transaction_tab(tab):
    """Setup the Borrow Transaction tab."""
    tk.Label(tab, text="Borrow Transaction", font=("Arial", 14, "bold")).pack(pady=10)

    # Frame for search by member ID
    search_frame = tk.Frame(tab)
    search_frame.pack(pady=10)

    tk.Label(search_frame, text="Member ID:").pack(side="left", padx=5)
    member_id_entry = tk.Entry(search_frame)
    member_id_entry.pack(side="left", padx=5)
    tk.Button(search_frame, text="Search", command=lambda: search_reservation(member_id_entry.get(), reservation_tree)).pack(side="left", padx=5)

    # Reserved Books List
    reserved_books_frame = tk.Frame(tab)
    reserved_books_frame.pack(pady=10)

    tk.Label(reserved_books_frame, text="Reserved Books", font=("Arial", 12, "bold")).pack(anchor="w", padx=10)
    global reservation_tree
    reservation_tree = ttk.Treeview(reserved_books_frame, columns=("isbn", "title"), show="headings")
    reservation_tree.heading("isbn", text="ISBN")
    reservation_tree.heading("title", text="Title")
    reservation_tree.pack(fill=tk.BOTH, expand=1, padx=10, pady=5)

    # Buttons to remove and transfer books
    button_frame = tk.Frame(tab)
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Remove", command=lambda: remove_from_reservation(reservation_tree)).pack(side="left", padx=5)
    tk.Button(button_frame, text="Transfer to Borrow", command=lambda: transfer_to_borrow(reservation_tree)).pack(side="left", padx=5)

def setup_reservation_tab(tab):
    """Setup the Reservation Tab."""
    tk.Label(tab, text="Reservation Management", font=("Arial", 14, "bold")).pack(pady=10)

    # Member ID Entry for Reservation Management
    search_frame = tk.Frame(tab)
    search_frame.pack(pady=10)

    tk.Label(search_frame, text="Member ID:").pack(side="left", padx=5)
    member_id_entry = tk.Entry(search_frame)
    member_id_entry.pack(side="left", padx=5)
    tk.Button(search_frame, text="Search", command=lambda: search_reservation(member_id_entry.get(), reservation_tree)).pack(side="left", padx=5)

    # Reserved Books List
    reserved_books_frame = tk.Frame(tab)
    reserved_books_frame.pack(pady=10)

    tk.Label(reserved_books_frame, text="Reserved Books", font=("Arial", 12, "bold")).pack(anchor="w", padx=10)
    global reservation_tree
    reservation_tree = ttk.Treeview(reserved_books_frame, columns=("isbn", "title"), show="headings")
    reservation_tree.heading("isbn", text="ISBN")
    reservation_tree.heading("title", text="Title")
    reservation_tree.pack(fill=tk.BOTH, expand=1, padx=10, pady=5)

def search_reservation(member_id, tree):
    """Search for reservations by member ID and update the reserved books list."""
    conn = connect_to_db()
    if conn is None:
        messagebox.showerror("Database Error", "Unable to connect to the database.")
        return

    cursor = conn.cursor()
    query = """
        SELECT ISBN, Title FROM tblReserveTransactions
        WHERE MemberID = ?
    """
    try:
        cursor.execute(query, (member_id,))
        reservations = cursor.fetchall()
        tree.delete(*tree.get_children())  # Clear previous results
        for reservation in reservations:
            tree.insert("", "end", values=(reservation[0], reservation[1]))
    except Exception as e:
        messagebox.showerror("Query Error", f"An error occurred: {e}")
    finally:
        conn.close()

def remove_from_reservation(tree):
    """Remove selected books from reservation list."""
    selected_items = tree.selection()
    if not selected_items:
        messagebox.showwarning("No Selection", "No items selected for removal.")
        return

    conn = connect_to_db()
    if conn is None:
        messagebox.showerror("Database Error", "Unable to connect to the database.")
        return

    cursor = conn.cursor()
    for item in selected_items:
        isbn = tree.item(item, "values")[0]
        try:
            cursor.execute("DELETE FROM tblReservations WHERE ISBN = ?", (isbn,))
            conn.commit()
            tree.delete(item)
        except Exception as e:
            messagebox.showerror("Query Error", f"An error occurred: {e}")
    
    conn.close()

def transfer_to_borrow(tree):
    """Transfer selected books from reservation to borrow records."""
    selected_items = tree.selection()
    if not selected_items:
        messagebox.showwarning("No Selection", "No items selected for transfer.")
        return

    conn = connect_to_db()
    if conn is None:
        messagebox.showerror("Database Error", "Unable to connect to the database.")
        return

    cursor = conn.cursor()
    member_id = "Some Member ID"  # Retrieve this from the relevant input field or context
    borrow_date = datetime.now().date()
    due_date = borrow_date + timedelta(days=14)  # Example due date, adjust as needed

    for item in selected_items:
        isbn = tree.item(item, "values")[0]
        try:
            cursor.execute("INSERT INTO tblBorrowTran (ISBN, MemberID, BorrowDate, DueDate) VALUES (?, ?, ?, ?)",
                           (isbn, member_id, borrow_date, due_date))
            cursor.execute("DELETE FROM tblReservations WHERE ISBN = ? AND MemberID = ?", (isbn, member_id))
            conn.commit()
            tree.delete(item)
        except Exception as e:
            messagebox.showerror("Query Error", f"An error occurred: {e}")
    
    conn.close()

def generate_report(member_id):
    """Generate a printable report for the borrowing transaction."""
    # Here, you should implement the logic to generate a report. This is a placeholder.
    report = f"""
    Borrow Report
    Date Borrowed: {datetime.now().date()}
    Due Date: {datetime.now().date() + timedelta(days=14)}
    Transaction Number: 12345  # Generate or fetch a real transaction number
    Member Name: Example Member
    Member ID: {member_id}
    Books Borrowed:
    - Example Book 1 (ISBN: 1234567890)
    - Example Book 2 (ISBN: 0987654321)
    """
    print(report)  # Replace with code to print or save the report

# Call the function to open the borrowing window
# open_borrowing_window() # Uncomment this line to test the window
