# search_and_reserve.py
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from db.database import connect_to_db

def book_reservation_window(role, username):
    """Open the book reservation window."""
    global filter_title_entry, filter_author_entry, filter_isbn_entry, abstract_text, category_combobox
    global search_results_treeview, cart_treeview
    global title_value, author_value, isbn_value, stock_value

    def add_to_cart():
        """Handle adding the selected book to the cart."""
        selected_item = search_results_treeview.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a book to add to the cart.")
            return

        item_values = search_results_treeview.item(selected_item, "values")
        title, isbn = item_values

        # Get stock value from stock_value label
        stock_text = stock_value.cget("text")
        try:
            stock = int(stock_text)
        except ValueError:
            messagebox.showwarning("Invalid Stock", f"Stock value '{stock_text}' is not valid.")
            return

        # Check if the book is in stock
        if stock <= 0:
            messagebox.showwarning("Out of Stock", "This book is out of stock and cannot be added to the cart.")
            return

        # Check if the book is already in the cart
        for item in cart_treeview.get_children():
            if cart_treeview.item(item, "values")[1] == isbn:
                messagebox.showwarning("Already in Cart", "This book is already in your cart.")
                return

        # Check if the cart is full
        if len(cart_treeview.get_children()) >= 3:
            messagebox.showwarning("Cart Limit Reached", "You can only add up to 3 books to your cart.")
            return

        cart_treeview.insert('', 'end', values=(title, isbn, stock))
        
    def remove_from_cart():
        """Handle removing the selected book from the cart."""
        selected_item = cart_treeview.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a book to remove from the cart.")
            return

        cart_treeview.delete(selected_item)

    def reserve_books():
        """Handle reserving books from the cart and saving to the tblReserveTransaction table."""
        if not cart_treeview.get_children():
            messagebox.showwarning("Empty Cart", "Your cart is empty. Please add books to the cart before reserving.")
            return

        conn = connect_to_db()
        if conn is None:
            messagebox.showerror("Database Error", "Unable to connect to the database.")
            return

        cursor = conn.cursor()

        try:
            # Fetch the UserID based on the username
            cursor.execute("SELECT UserID FROM tblUsers WHERE Uname = ?", (username,))
            user_id = cursor.fetchone()
            if user_id is None:
                messagebox.showerror("User Error", "User not found.")
                return

            user_id = user_id[0]

            cursor.execute("SELECT ISNULL(MAX(TransactionNo), 0) + 1 FROM tblReserveTransaction")
            new_transaction_no = cursor.fetchone()[0]

            # Use the username in the Notes field
            notes = f"Reserved by {username}"

            for item in cart_treeview.get_children():
                title, isbn, stock = cart_treeview.item(item, "values")
                if int(stock) <= 0:
                    messagebox.showwarning("Out of Stock", f"The book '{title}' is out of stock and cannot be reserved.")
                    return

                query = """
                INSERT INTO tblReserveTransaction (UserID, TransactionNo, DateReserved, ISBN, Notes)
                VALUES (?, ?, GETDATE(), ?, ?)
                """
                cursor.execute(query, (user_id, new_transaction_no, isbn, notes))

            conn.commit()
            messagebox.showinfo("Reservation Successful", "Books reserved successfully!")
            cart_treeview.delete(*cart_treeview.get_children())

        except Exception as e:
            conn.rollback()
            messagebox.showerror("Reservation Error", f"An error occurred while reserving books: {e}")
        finally:
            conn.close()

    def search_books(title, author, isbn, category):
        """Search for books in the database and update search results treeview."""
        conn = connect_to_db()
        if conn is None:
            messagebox.showerror("Database Error", "Unable to connect to the database.")
            return

        cursor = conn.cursor()
        query = "SELECT * FROM tblBooks WHERE 1=1"
        if category and category != "All":
            query += f" AND Category='{category}'"
        if title:
            query += f" AND Title LIKE '%{title}%'"
        if author:
            query += f" AND Author LIKE '%{author}%'"
        if isbn:
            query += f" AND ISBN='{isbn}'"

        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            if rows:
                search_results_treeview.delete(*search_results_treeview.get_children())
                for row in rows:
                    search_results_treeview.insert('', 'end', values=(row[1], row[0]))  # Display Title and ISBN
            else:
                messagebox.showinfo("No Results", "No books found matching the criteria.")
        except Exception as e:
            messagebox.showerror("Query Error", f"An error occurred: {e}")
        finally:
            conn.close()

    def on_search_results_select(event):
        """Populate the book information fields when a search result is selected."""
        selected_item = search_results_treeview.selection()
        if selected_item:
            item_values = search_results_treeview.item(selected_item, "values")
            title, isbn = item_values

            conn = connect_to_db()
            if conn is None:
                messagebox.showerror("Database Error", "Unable to connect to the database.")
                return

            cursor = conn.cursor()
            query = "SELECT * FROM tblBooks WHERE ISBN = ?"
            cursor.execute(query, (isbn,))
            book = cursor.fetchone()

            if book:
                title_value.config(text=book[1])
                author_value.config(text=book[2])
                isbn_value.config(text=book[0])
                stock_value.config(text=str(book[10]))  # Assuming stock is in the 10th index
                abstract_text.config(state=tk.NORMAL)
                abstract_text.delete(1.0, tk.END)
                abstract_text.insert(tk.END, book[4])  # Assuming abstract is in the 4th index
                abstract_text.config(state=tk.DISABLED)
            else:
                messagebox.showwarning("No Data", "No detailed data found for the selected book.")
        else:
            title_value.config(text="")
            author_value.config(text="")
            isbn_value.config(text="")
            stock_value.config(text="")
            abstract_text.config(state=tk.NORMAL)
            abstract_text.delete(1.0, tk.END)
            abstract_text.config(state=tk.DISABLED)

    # Create the main window and its widgets
    reservation_window = tk.Toplevel()
    reservation_window.title("Book Reservation")
    reservation_window.geometry("1200x800")

    # Book information (Left Side)
    book_info_frame = tk.Frame(reservation_window, padx=10, pady=10)
    book_info_frame.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="nsew")

    tk.Label(book_info_frame, text="Title:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
    title_value = tk.Label(book_info_frame, text="", width=40, anchor=tk.W)
    title_value.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

    tk.Label(book_info_frame, text="Author:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
    author_value = tk.Label(book_info_frame, text="", width=40, anchor=tk.W)
    author_value.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

    tk.Label(book_info_frame, text="ISBN:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.E)
    isbn_value = tk.Label(book_info_frame, text="", width=40, anchor=tk.W)
    isbn_value.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

    tk.Label(book_info_frame, text="Stock:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.E)
    stock_value = tk.Label(book_info_frame, text="", width=40, anchor=tk.W)
    stock_value.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)

    tk.Label(book_info_frame, text="Abstract:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.N)
    abstract_text = scrolledtext.ScrolledText(book_info_frame, width=40, height=10, wrap=tk.WORD, state=tk.DISABLED)
    abstract_text.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)

    # Filter and Search (Right Side)
    filter_frame = tk.Frame(reservation_window, padx=10, pady=10)
    filter_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

    tk.Label(filter_frame, text="Category:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
    category_combobox = ttk.Combobox(filter_frame, values=["All", "Fiction", "Non-Fiction", "Science", "History", "Biography"])
    category_combobox.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
    category_combobox.set("All")

    tk.Label(filter_frame, text="Title:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
    filter_title_entry = tk.Entry(filter_frame)
    filter_title_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

    tk.Label(filter_frame, text="Author:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.E)
    filter_author_entry = tk.Entry(filter_frame)
    filter_author_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

    tk.Label(filter_frame, text="ISBN:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.E)
    filter_isbn_entry = tk.Entry(filter_frame)
    filter_isbn_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)

    tk.Button(filter_frame, text="Search", command=lambda: search_books(
        filter_title_entry.get(), filter_author_entry.get(), filter_isbn_entry.get(), category_combobox.get()), width=20).grid(row=4, column=0, columnspan=2, padx=10, pady=10)

    # Search results (Below Book Information)
    search_results_frame = tk.Frame(reservation_window, padx=10, pady=10)
    search_results_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

    tk.Label(search_results_frame, text="Search Results").pack()

    search_results_treeview = ttk.Treeview(search_results_frame, columns=("Title", "ISBN"), show="headings")
    search_results_treeview.heading("Title", text="Title")
    search_results_treeview.heading("ISBN", text="ISBN")
    search_results_treeview.pack(fill=tk.BOTH, expand=True)
    search_results_treeview.bind("<<TreeviewSelect>>", on_search_results_select)

    # Cart (Beside Search Results)
    cart_frame = tk.Frame(reservation_window, padx=10, pady=10)
    cart_frame.grid(row=2, column=2, padx=10, pady=10, sticky="nsew")

    tk.Label(cart_frame, text="Cart").pack()

    cart_treeview = ttk.Treeview(cart_frame, columns=("Title", "ISBN", "Stock"), show="headings")
    cart_treeview.heading("Title", text="Title")
    cart_treeview.heading("ISBN", text="ISBN")
    cart_treeview.heading("Stock", text="Stock")
    cart_treeview.pack(fill=tk.BOTH, expand=True)

    # Buttons
    button_frame = tk.Frame(reservation_window, padx=10, pady=10)
    button_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

    tk.Button(button_frame, text="Add to Cart", command=add_to_cart, width=20).grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
    tk.Button(button_frame, text="Remove from Cart", command=remove_from_cart, width=20).grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)
    tk.Button(button_frame, text="Reserve", command=reserve_books, width=20).grid(row=0, column=2, padx=10, pady=10, sticky=tk.W)

    # Adjust column and row weights for resizing
    reservation_window.grid_columnconfigure(0, weight=1)
    reservation_window.grid_columnconfigure(1, weight=1)
    reservation_window.grid_columnconfigure(2, weight=1)
    reservation_window.grid_rowconfigure(0, weight=1)
    reservation_window.grid_rowconfigure(1, weight=1)
    reservation_window.grid_rowconfigure(2, weight=1)
    reservation_window.grid_rowconfigure(3, weight=1)

    reservation_window.mainloop()

# Example usage
# book_reservation_window("user_role", "username")
