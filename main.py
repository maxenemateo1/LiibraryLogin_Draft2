import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from login import open_login_window
from database import connect_to_db
from datetime import datetime


class BookManager:
    def __init__(self, root):
        self.root = root
        self.root.title("ABC Learning Resource Center")
        self.root.geometry("900x600")

        self.current_book_index = -1
        self.rows = []

        # Setup UI components
        self.setup_main_window()

    def update_book_info(self, book):
        """Update the book information labels."""
        if not book:
            return
        self.title_value.config(text=book[1])
        self.author_value.config(text=book[2])
        self.isbn_value.config(text=book[0])
        self.stock_value.config(text=str(book[4]))  # Assuming stock is in the 5th column
        self.abstract_text.delete('1.0', tk.END)
        self.abstract_text.insert(tk.END, book[3])  # Assuming abstract is in the 4th column

    def search_books(self):
        """Search books based on input filters."""
        category = self.category_combobox.get()
        title = self.title_entry.get()
        author = self.author_entry.get()
        isbn = self.isbn_entry.get()

        conn = connect_to_db()
        if conn is None:
            return

        cursor = conn.cursor()

        # SQL query construction based on inputs
        query = """
        SELECT ISBN, Title, Author, Abstract, InStock
        FROM tblBooks
        WHERE 1=1
        """
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
            self.rows = cursor.fetchall()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            self.rows = []

        self.book_listbox.delete(0, tk.END)  # Clear previous search results
        if not self.rows:
            self.book_listbox.insert(tk.END, "No results found.")
            self.update_book_info(("", "", "", "", 0))
        else:
            for row in self.rows:
                self.book_listbox.insert(tk.END, row[1])  # Assuming title is in the 2nd column
            self.display_book(0)

        conn.close()

    def display_book(self, index):
        """Display the selected book's details."""
        if 0 <= index < len(self.rows):
            self.update_book_info(self.rows[index])
            self.current_book_index = index
        else:
            self.update_book_info(("", "", "", "", 0))

    def prev_book(self):
        """Display the previous book in the list."""
        if len(self.rows) > 0 and self.current_book_index > 0:
            self.display_book(self.current_book_index - 1)

    def next_book(self):
        """Display the next book in the list."""
        if len(self.rows) > 0 and self.current_book_index < len(self.rows) - 1:
            self.display_book(self.current_book_index + 1)

    def setup_main_window(self):
        """Setup the main window and its components."""
        # Header Frame
        header_frame = tk.Frame(self.root, bg="white", relief=tk.RIDGE, borderwidth=2)
        header_frame.pack(fill=tk.X, padx=10, pady=5)

        # Title Label
        title_label = tk.Label(header_frame, text="ABC Learning Resource Center", font=("Arial", 18, "bold"), bg="white")
        title_label.pack(side=tk.LEFT, padx=10)

        # Welcome and Sign In
        welcome_label = tk.Label(header_frame, text="Welcome Guest!", font=("Arial", 12), bg="white")
        welcome_label.pack(side=tk.RIGHT, padx=10)

        sign_in_button = tk.Button(header_frame, text="Sign In", font=("Arial", 10), command=open_login_window)
        sign_in_button.pack(side=tk.RIGHT, padx=10)

        # Tabs for Search and Reserve / Transaction Record
        tab_control = ttk.Notebook(self.root)
        search_tab = ttk.Frame(tab_control)
        transaction_tab = ttk.Frame(tab_control)

        tab_control.add(search_tab, text="Search and Reserve")
        tab_control.add(transaction_tab, text="Transaction Record")
        tab_control.pack(fill=tk.BOTH, expand=1, padx=10, pady=5)

        # Main content frame
        content_frame = tk.Frame(search_tab, relief=tk.RIDGE, borderwidth=2)
        content_frame.pack(fill=tk.BOTH, expand=1, padx=10, pady=10)

        # Book List Section (Left)
        book_list_frame = tk.Frame(content_frame, relief=tk.GROOVE, borderwidth=2, bg="white")
        book_list_frame.grid(row=0, column=0, sticky="ns", padx=10, pady=10)

        book_list_label = tk.Label(book_list_frame, text="Book List", font=("Arial", 12, "bold"), bg="white")
        book_list_label.pack(padx=10, pady=5)

        self.book_listbox = tk.Listbox(book_list_frame, height=20, width=50)
        self.book_listbox.pack(padx=10, pady=10)

        self.book_listbox.bind('<<ListboxSelect>>', self.on_listbox_select)

        # Book Information Section (Right)
        book_info_frame = tk.Frame(content_frame, relief=tk.GROOVE, borderwidth=2, bg="white")
        book_info_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        book_info_label = tk.Label(book_info_frame, text="Book Information", font=("Arial", 12, "bold"), bg="white")
        book_info_label.grid(row=0, column=0, padx=10, pady=5, sticky="w", columnspan=2)

        # Book Details
        title_label = tk.Label(book_info_frame, text="Title", bg="white")
        title_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")

        author_label = tk.Label(book_info_frame, text="Author", bg="white")
        author_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")

        isbn_label = tk.Label(book_info_frame, text="ISBN", bg="white")
        isbn_label.grid(row=3, column=0, padx=10, pady=5, sticky="e")

        stock_label = tk.Label(book_info_frame, text="Stock", bg="white")
        stock_label.grid(row=4, column=0, padx=10, pady=5, sticky="e")

        # Text Entries for Book Information
        self.title_value = tk.Label(book_info_frame, bg="white", width=30, relief=tk.SUNKEN)
        self.title_value.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        self.author_value = tk.Label(book_info_frame, bg="white", width=30, relief=tk.SUNKEN)
        self.author_value.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        self.isbn_value = tk.Label(book_info_frame, bg="white", width=30, relief=tk.SUNKEN)
        self.isbn_value.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        self.stock_value = tk.Label(book_info_frame, bg="white", width=30, relief=tk.SUNKEN)
        self.stock_value.grid(row=4, column=1, padx=10, pady=5, sticky="w")

        # Abstract Section
        abstract_label = tk.Label(book_info_frame, text="Abstract", bg="white")
        abstract_label.grid(row=5, column=0, padx=10, pady=5, sticky="nw")

        self.abstract_text = tk.Text(book_info_frame, height=5, width=30, wrap="word", relief=tk.SUNKEN, bg="white")
        self.abstract_text.grid(row=5, column=1, padx=10, pady=5, sticky="w")

        # Navigation Buttons (Bottom)
        nav_frame = tk.Frame(book_info_frame, bg="white")
        nav_frame.grid(row=6, column=1, pady=10, sticky="w")

        prev_button = tk.Button(nav_frame, text="<<", relief=tk.GROOVE, width=3, command=self.prev_book)
        prev_button.pack(side="left", padx=5)
        next_button = tk.Button(nav_frame, text=">>", relief=tk.GROOVE, width=3, command=self.next_book)
        next_button.pack(side="left", padx=5)

        # Filter Section (Right)
        filter_frame = tk.Frame(content_frame, relief=tk.GROOVE, borderwidth=2, bg="white")
        filter_frame.grid(row=0, column=2, sticky="nsew", padx=(10, 0), pady=10)

        filter_label = tk.Label(filter_frame, text="Filter", font=("Arial", 12, "bold"), bg="white")
        filter_label.pack(anchor="w", padx=10, pady=5)

        # Category Filter
        category_label = tk.Label(filter_frame, text="Category", bg="white")
        category_label.pack(anchor="w", padx=10)
        self.category_combobox = ttk.Combobox(filter_frame, values=[
            "All", "Communication", "Electronic media", "Mechatronics", "Databases",
            "Electronics Engineering", "Web Design", "Automotive", "Electronics",
            "Plumbing", "Game Art", "Programming", "Utilities", "Networking",
            "Game Design", "Game Programming", "ICT"
        ])
        self.category_combobox.pack(anchor="w", padx=10, pady=5)

        # Title Filter
        title_label = tk.Label(filter_frame, text="Title", bg="white")
        title_label.pack(anchor="w", padx=10)
        self.title_entry = tk.Entry(filter_frame)
        self.title_entry.pack(anchor="w", padx=10, pady=5)

        # Author Filter
        author_label = tk.Label(filter_frame, text="Author", bg="white")
        author_label.pack(anchor="w", padx=10)
        self.author_entry = tk.Entry(filter_frame)
        self.author_entry.pack(anchor="w", padx=10, pady=5)

        # ISBN Filter
        isbn_label = tk.Label(filter_frame, text="ISBN", bg="white")
        isbn_label.pack(anchor="w", padx=10)
        self.isbn_entry = tk.Entry(filter_frame)
        self.isbn_entry.pack(anchor="w", padx=10, pady=5)

        # Search Button
        search_button = tk.Button(filter_frame, text="Search", command=self.search_books, relief=tk.GROOVE)
        search_button.pack(pady=10, padx=10)

    def on_listbox_select(self, event):
        """Handle listbox selection."""
        selected_index = self.book_listbox.curselection()
        if selected_index:
            self.display_book(selected_index[0])

if __name__ == "__main__":
    root = tk.Tk()
    app = BookManager(root)
    root.mainloop()
