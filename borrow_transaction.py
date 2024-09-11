import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from database import connect_to_db

def borrow_transaction_window(role, username):
    # Create the main window
    root = tk.Toplevel()
    root.title("ABC Learning Resource Center")
    root.geometry("800x500")

    # Top frame for the title and user info
    top_frame = tk.Frame(root)
    top_frame.pack(side=tk.TOP, fill=tk.X)

    title_label = tk.Label(top_frame, text="ABC Learning Resource Center", font=("Arial", 16))
    title_label.pack(side=tk.LEFT, padx=10, pady=10)

    welcome_label = tk.Label(top_frame, text=f"Welcome {username}!", font=("Arial", 12))
    welcome_label.pack(side=tk.RIGHT, padx=10)

    user_info_label = tk.Label(top_frame, text=f"You're logged in as {role.capitalize()}", font=("Arial", 10))
    user_info_label.pack(side=tk.RIGHT, padx=10)

    # Logout button
    logout_button = tk.Button(top_frame, text="Log out", command=root.destroy)
    logout_button.pack(side=tk.RIGHT, padx=10, pady=10)

    # Notebook for tabs
    notebook = ttk.Notebook(root)
    notebook.pack(pady=10, expand=True)

    # Create frames for each tab
    borrow_tab = tk.Frame(notebook, width=800, height=400)
    return_tab = tk.Frame(notebook, width=800, height=400)
    admin_tab = tk.Frame(notebook, width=800, height=400)

    borrow_tab.pack(fill='both', expand=True)
    return_tab.pack(fill='both', expand=True)
    admin_tab.pack(fill='both', expand=True)

    # Add tabs to the notebook
    notebook.add(borrow_tab, text='Borrow Transactions')
    notebook.add(return_tab, text='Return Transactions')
    notebook.add(admin_tab, text='Administrative Transactions')

    # Sub-notebook for "Manual Entry" and "Reservation"
    sub_notebook = ttk.Notebook(borrow_tab)
    sub_notebook.pack(pady=10, expand=True)

    manual_entry_frame = tk.Frame(sub_notebook, width=800, height=350)
    reservation_frame = tk.Frame(sub_notebook, width=800, height=350)

    manual_entry_frame.pack(fill='both', expand=True)
    reservation_frame.pack(fill='both', expand=True)

    sub_notebook.add(manual_entry_frame, text='Manual Entry')
    sub_notebook.add(reservation_frame, text='Reservation')

    # Search section in the "Manual Entry" tab
    search_frame = tk.Frame(manual_entry_frame)
    search_frame.pack(pady=10)

    search_label = tk.Label(search_frame, text="Enter Member's ID No.:")
    search_label.grid(row=0, column=0, padx=5)

    search_entry = tk.Entry(search_frame)
    search_entry.grid(row=0, column=1, padx=5)

    search_button = tk.Button(search_frame, text="Search", command=lambda: search_transactions(search_entry.get().strip(), tree))
    search_button.grid(row=0, column=2, padx=5)

    # Table-like structure to display search results
    results_frame = tk.Frame(manual_entry_frame)
    results_frame.pack(pady=10, fill='both', expand=True)

    # Treeview setup to display Title, ISBN, and Status
    tree = ttk.Treeview(results_frame, columns=("Title", "ISBN", "Status"), show='headings')
    tree.heading("Title", text="Title")
    tree.heading("ISBN", text="ISBN")
    tree.heading("Status", text="Status")

    # Adjust the column width for better visibility
    tree.column("Title", width=500, anchor=tk.W)
    tree.column("ISBN", width=150, anchor=tk.W)
    tree.column("Status", width=100, anchor=tk.W)

    tree.pack(fill='both', expand=True)

    # Buttons for actions
    action_frame = tk.Frame(manual_entry_frame)
    action_frame.pack(pady=10)

    lend_button = tk.Button(action_frame, text="Lend selected books", command=lambda: lend_books(search_entry.get().strip(), tree))
    lend_button.grid(row=0, column=0, padx=5)

    remove_button = tk.Button(action_frame, text="Remove selected books", command=lambda: remove_books(tree))
    remove_button.grid(row=0, column=1, padx=5)

    print_button = tk.Button(action_frame, text="Print Receipt", command=lambda: print_receipt(search_entry.get().strip(), tree))
    print_button.grid(row=0, column=2, padx=5)

    def search_transactions(member_id, tree):
        """Search all transactions by member ID and populate the Treeview with book titles, ISBNs, and status."""
        if not member_id.isdigit():
            messagebox.showerror("Input Error", "Member ID must be a valid number.")
            return

        conn = connect_to_db()
        if conn is None:
            messagebox.showerror("Connection Error", "Could not connect to the database.")
            return

        cursor = conn.cursor()
        query = """
        SELECT b.Title, r.ISBN, 
               CASE 
                   WHEN EXISTS (SELECT 1 FROM tblBorrowTran bt WHERE bt.ISBN = r.ISBN AND bt.UserID = r.UserID) 
                   THEN 'Lent'
                   ELSE 'Reserved'
               END AS Status
        FROM tblReserveTransaction r
        JOIN tblBooks b ON r.ISBN = b.ISBN
        WHERE r.UserID = ?
        UNION
        SELECT b.Title, bt.ISBN, 'Lent' AS Status
        FROM tblBorrowTran bt
        JOIN tblBooks b ON bt.ISBN = b.ISBN
        WHERE bt.UserID = ?
        """
        try:
            cursor.execute(query, (member_id, member_id))
            results = cursor.fetchall()
            tree.delete(*tree.get_children())  # Clear previous results

            # Populate the treeview with search results
            for row in results:
                if len(row) == 3:  # Ensure correct data structure
                    tree.insert('', 'end', values=(row[0], row[1], row[2]))

            global borrower_name  # Set the borrower's name globally
            borrower_name = results[0][2] if results else "Unknown"

        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
        finally:
            conn.close()

    def lend_books(member_id, tree):
        """Transfer reserved books to borrowed transactions for the given member ID."""
        selected_items = tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "No items selected to lend.")
            return

        items = [tree.item(item, 'values') for item in selected_items]

        conn = connect_to_db()
        if conn is None:
            messagebox.showerror("Connection Error", "Could not connect to the database.")
            return

        cursor = conn.cursor()
        borrow_query = """
        INSERT INTO tblBorrowTran (UserID, TransactionNo, DateBorrowed, ISBN, IsBookReturned, Notes) 
        VALUES (?, ?, ?, ?, ?, ?)
        """
        reserve_query = """
        DELETE FROM tblReserveTransaction
        WHERE ISBN = ? AND UserID = ?
        """

        try:
            for idx, item in enumerate(items):
                title, isbn, status = item
                transaction_no = idx + 1  # Example transaction number; adjust logic as needed

                # Insert into tblBorrowTran
                cursor.execute(borrow_query, (int(member_id), transaction_no, datetime.now(), isbn, False, ''))
                # Remove from tblReserveTransaction
                cursor.execute(reserve_query, (isbn, int(member_id)))

                # Update the status in the treeview
                tree.item(tree.selection()[idx], values=(title, isbn, 'Lent'))

            conn.commit()
            messagebox.showinfo("Success", "Books successfully lent.")
            
            # Print the receipt after lending books
            print_receipt(member_id, tree)

        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
        finally:
            conn.close()

    def remove_books(tree):
        """Remove selected books from the Treeview."""
        selected_items = tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "No items selected to remove.")
            return

        for item in selected_items:
            tree.delete(item)

    def print_receipt(member_id, tree):
        """Open a new window to display the formatted receipt."""
        receipt_window = tk.Toplevel(root)
        receipt_window.title("Receipt")
        receipt_window.geometry("400x400")

        receipt_text = tk.Text(receipt_window, wrap=tk.WORD)
        receipt_text.pack(expand=True, fill='both')

        # Gather information for the receipt
        date_borrowed = datetime.now().strftime("%d-%B-%Y")
        due_date = (datetime.now() + timedelta(days=7)).strftime("%d-%B-%Y")

        # Header information
        receipt_info = f"""
ABC Learning Resource Center
Date Borrowed: {date_borrowed}
Date Due: {due_date}
Transaction No.: {member_id}

Title                       ISBN
---------------------------------
"""
        # Fetch data from Treeview for selected books
        for item in tree.get_children():
            title, isbn, status = tree.item(item, 'values')
            receipt_info += f"{title[:25]:25} {isbn}\n"

        # Footer information
        receipt_info += f"""
---------------------------------
This is to certify that I received the books above in good condition and agree to pay the corresponding penalties of Php 20.00/day per book if not returned within the due date. I also agree to pay the corresponding book amount in case I lose possession of the book.

{borrower_name}
Signature
"""

        # Display receipt information in the Text widget
        receipt_text.insert(tk.END, receipt_info)

    def populate_reservation_frame():
        """Populate the reservation_frame with all reserved and lent books."""
        conn = connect_to_db()
        if conn is None:
            messagebox.showerror("Connection Error", "Could not connect to the database.")
            return

        cursor = conn.cursor()
        query = """
        SELECT b.Title, r.ISBN, 'Reserved' AS Status
        FROM tblReserveTransaction r
        JOIN tblBooks b ON r.ISBN = b.ISBN
        UNION
        SELECT b.Title, bt.ISBN, 'Lent' AS Status
        FROM tblBorrowTran bt
        JOIN tblBooks b ON bt.ISBN = b.ISBN
        """
        try:
            cursor.execute(query)
            results = cursor.fetchall()
            tree_reservation.delete(*tree_reservation.get_children())  # Clear previous results

            # Populate the treeview with search results
            for row in results:
                if len(row) == 3:  # Ensure correct data structure
                    tree_reservation.insert('', 'end', values=(row[0], row[1], row[2]))

        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
        finally:
            conn.close()

    # Treeview setup to display all reservations and borrowed books
    reservation_results_frame = tk.Frame(reservation_frame)
    reservation_results_frame.pack(pady=10, fill='both', expand=True)

    tree_reservation = ttk.Treeview(reservation_results_frame, columns=("Title", "ISBN", "Status"), show='headings')
    tree_reservation.heading("Title", text="Title")
    tree_reservation.heading("ISBN", text="ISBN")
    tree_reservation.heading("Status", text="Status")

    # Adjust the column width for better visibility
    tree_reservation.column("Title", width=500, anchor=tk.W)
    tree_reservation.column("ISBN", width=150, anchor=tk.W)
    tree_reservation.column("Status", width=100, anchor=tk.W)

    tree_reservation.pack(fill='both', expand=True)

    # Populate the reservation frame initially
    populate_reservation_frame()

    root.mainloop()

if __name__ == "__main__":
    borrow_transaction_window("admin", "admin1")  # Use a valid role and user ID for testing
