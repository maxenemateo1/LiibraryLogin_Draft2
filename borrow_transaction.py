import tkinter as tk
from tkinter import messagebox, ttk
from database import connect_to_db
from datetime import datetime, timedelta

def setup_borrowing_transaction_facility(parent_window, username):
    """Sets up the borrowing transaction facility UI in a given parent window."""
    
    def search_transactions():
        """Searches for borrowing transactions based on Member ID."""
        member_id = member_id_entry.get()
        if not member_id:
            messagebox.showwarning("Input Error", "Please enter a Member ID.")
            return

        conn = connect_to_db()
        if conn is None:
            messagebox.showerror("Database Error", "Unable to connect to the database.")
            return

        cursor = conn.cursor()
        
        # Fetch member's name
        cursor.execute("SELECT Uname FROM tblUsers WHERE UserID = ?", (member_id,))
        member_name_result = cursor.fetchone()
        if member_name_result:
            member_name = member_name_result[0]
        else:
            messagebox.showwarning("Member Not Found", "No member found with the given ID.")
            conn.close()
            return

        # Fetch transactions
        query = """
            SELECT Title, ISBN
            FROM tblBorrowTran bt
            JOIN tblBooks b ON bt.ISBN = b.ISBN
            WHERE bt.UserID = ?
            AND bt.IsBookReturned = 0
        """
        try:
            cursor.execute(query, (member_id,))
            rows = cursor.fetchall()
            if rows:
                transactions_treeview.delete(*transactions_treeview.get_children())  # Clear previous search results
                for row in rows:
                    transactions_treeview.insert('', 'end', values=(row[0], row[1]))
            else:
                messagebox.showinfo("No Results", "No transactions found for the given Member ID.")
        except Exception as e:
            messagebox.showerror("Query Error", f"An error occurred: {e}")
        finally:
            conn.close()

    def lend_books():
        """Lends the books and generates a printable report."""
        selected_items = transactions_treeview.selection()
        if not selected_items:
            messagebox.showwarning("Selection Error", "Please select books to lend.")
            return

        member_id = member_id_entry.get()
        if not member_id:
            messagebox.showwarning("Input Error", "Please enter a Member ID.")
            return

        conn = connect_to_db()
        if conn is None:
            messagebox.showerror("Database Error", "Unable to connect to the database.")
            return

        cursor = conn.cursor()
        
        # Fetch member's name again
        cursor.execute("SELECT Uname FROM tblUsers WHERE UserID = ?", (member_id,))
        member_name_result = cursor.fetchone()
        member_name = member_name_result[0] if member_name_result else "Unknown"

        transaction_number = f"T{datetime.now().strftime('%Y%m%d%H%M%S')}"
        date_borrowed = datetime.now().strftime("%Y-%m-%d")
        due_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")  # Assuming 2 weeks due date

        report_text = (
            f"ABC LEARNING RESOURCE CENTER\n"
            f"Date Borrowed: {date_borrowed}\n"
            f"Transaction No: {transaction_number}\n"
            f"Date Due: {due_date}\n"
            f"Member's Name: {member_name}\n"
            f"Member's ID: {member_id}\n\n"
            f"Books Borrowed:\n"
        )

        books = []
        for item in selected_items:
            book_title, book_isbn = transactions_treeview.item(item, 'values')
            books.append((book_title, book_isbn))

            # Update the database to mark books as borrowed
            cursor.execute("UPDATE tblBorrowTran SET TransactionNo = ?, DateBorrowed = ?, IsBookReturned = 0 WHERE ISBN = ? AND UserID = ?",
                           (transaction_number, date_borrowed, book_isbn, member_id))

        for title, isbn in books:
            report_text += f"{title} | {isbn}\n"

        report_text += "\nThank you for using our library!"

        # Display the report
        report_window = tk.Toplevel(parent_window)
        report_window.title("Borrowing Transaction Report")
        report_window.geometry("400x400")

        report_label = tk.Label(report_window, text="Generated Printable Report", font=("Arial", 12, "bold"))
        report_label.pack(pady=10)

        report_textbox = tk.Text(report_window, wrap=tk.WORD)
        report_textbox.insert(tk.END, report_text)
        report_textbox.config(state=tk.DISABLED)  # Make the text box read-only
        report_textbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        close_button = tk.Button(report_window, text="Close", command=report_window.destroy)
        close_button.pack(side=tk.LEFT, padx=10, pady=10)

        print_button = tk.Button(report_window, text="Print", command=lambda: print_report(report_text))
        print_button.pack(side=tk.RIGHT, padx=10, pady=10)

        conn.commit()
        conn.close()

    def print_report(report_text):
        """Prints the report."""
        try:
            # This method is just a placeholder. Implement actual print functionality if required.
            print("Printing report...")
            print(report_text)
            messagebox.showinfo("Print", "Report sent to printer.")
        except Exception as e:
            messagebox.showerror("Print Error", f"An error occurred while printing: {e}")

    # Main window setup
    parent_window.title("Borrowing Transaction Facility")

    header_label = tk.Label(parent_window, text="ABC LEARNING RESOURCE CENTER", font=("Arial", 16, "bold"))
    header_label.pack(pady=10)

    welcome_label = tk.Label(parent_window, text=f"Welcome, {username}!", anchor="e", padx=20)
    welcome_label.pack(fill=tk.X)

    tab_control = ttk.Notebook(parent_window)
    tab_control.pack(fill=tk.BOTH, expand=1)

    # Transaction Record Tab
    transaction_tab = tk.Frame(tab_control)
    tab_control.add(transaction_tab, text="Transaction Record")

    search_frame = tk.Frame(transaction_tab)
    search_frame.pack(pady=10, padx=10, fill=tk.X)

    tk.Label(search_frame, text="Enter Member's ID No:").pack(side=tk.LEFT)
    member_id_entry = tk.Entry(search_frame)
    member_id_entry.pack(side=tk.LEFT, padx=5)

    search_button = tk.Button(search_frame, text="Search", command=search_transactions)
    search_button.pack(side=tk.LEFT, padx=5)

    transactions_frame = tk.Frame(transaction_tab)
    transactions_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=1)

    transactions_treeview = ttk.Treeview(transactions_frame, columns=("Title", "ISBN"), show='headings')
    transactions_treeview.heading("Title", text="Title")
    transactions_treeview.heading("ISBN", text="ISBN")
    transactions_treeview.column("Title", width=200)
    transactions_treeview.column("ISBN", width=100)
    transactions_treeview.pack(fill=tk.BOTH, expand=1)

    lend_buttons_frame = tk.Frame(transaction_tab)
    lend_buttons_frame.pack(pady=10, padx=10, fill=tk.X)

    remove_button = tk.Button(lend_buttons_frame, text="Remove Selected Item", command=lambda: transactions_treeview.delete(transactions_treeview.selection()))
    remove_button.pack(side=tk.LEFT, padx=5)

    lend_button = tk.Button(lend_buttons_frame, text="Lend Listed Books", command=lend_books)
    lend_button.pack(side=tk.LEFT, padx=5)

# Note: Ensure you have appropriate imports and that `connect_to_db` function is defined in `database.py`.
