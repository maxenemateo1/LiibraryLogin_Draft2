import tkinter as tk
from tkinter import messagebox, ttk
from database import connect_to_db

# Global variables for search results and current book index
rows = []
current_book_index = -1

def setup_search_tab(tab, role, username):
    global category_combobox, title_entry, author_entry, isbn_entry
    global book_info_frame, title_value, author_value, isbn_value, stock_value, abstract_text
    global prev_button, next_button, search_results_treeview

    # Frame for search and filter
    search_tab_frame = tk.Frame(tab, bg="white")
    search_tab_frame.pack(fill=tk.BOTH, expand=1, padx=10, pady=10)

    # Filter Section
    filter_frame = tk.Frame(search_tab_frame, relief=tk.GROOVE, borderwidth=2, bg="white")
    filter_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

    filter_label = tk.Label(filter_frame, text="Filter", font=("Arial", 12, "bold"), bg="white")
    filter_label.pack(anchor="w", padx=10, pady=5)

    # Category Filter
    category_label = tk.Label(filter_frame, text="Category", bg="white")
    category_label.pack(anchor="w", padx=10)
    category_combobox = ttk.Combobox(filter_frame, values=[
        "All", "Communication", "Electronic media", "Mechatronics", "Databases",
        "Electronics Engineering", "Web Design", "Automotive", "Electronics",
        "Plumbing", "Game Art", "Programming", "Utilities", "Networking",
        "Game Design", "Game Programming", "ICT"
    ])
    category_combobox.set("All")
    category_combobox.pack(anchor="w", padx=10, pady=5)

    # Title Filter
    title_label = tk.Label(filter_frame, text="Title", bg="white")
    title_label.pack(anchor="w", padx=10)
    title_entry = tk.Entry(filter_frame)
    title_entry.pack(anchor="w", padx=10, pady=5)

    # Author Filter
    author_label = tk.Label(filter_frame, text="Author", bg="white")
    author_label.pack(anchor="w", padx=10)
    author_entry = tk.Entry(filter_frame)
    author_entry.pack(anchor="w", padx=10, pady=5)

    # ISBN Filter
    isbn_label = tk.Label(filter_frame, text="ISBN", bg="white")
    isbn_label.pack(anchor="w", padx=10)
    isbn_entry = tk.Entry(filter_frame)
    isbn_entry.pack(anchor="w", padx=10, pady=5)

    # Search Button
    search_button = tk.Button(filter_frame, text="Search", command=search_books_action, relief=tk.GROOVE)
    search_button.pack(pady=10, padx=10)

    # Search Results Section
    results_frame = tk.Frame(search_tab_frame, relief=tk.GROOVE, borderwidth=2, bg="white")
    results_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=1, padx=10, pady=10)

    search_results_label = tk.Label(results_frame, text="Search Results", font=("Arial", 12, "bold"), bg="white")
    search_results_label.pack(anchor="w", padx=10, pady=5)

    search_results_treeview = ttk.Treeview(results_frame, columns=("Title", "ISBN"), show='headings')
    search_results_treeview.heading("Title", text="Title")
    search_results_treeview.heading("ISBN", text="ISBN")
    search_results_treeview.pack(fill=tk.BOTH, expand=1, padx=10, pady=5)
    search_results_treeview.bind("<<TreeviewSelect>>", on_treeview_select)

    # Book Information Section
    book_info_frame = tk.Frame(search_tab_frame, relief=tk.GROOVE, borderwidth=2, bg="white")
    book_info_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=1, padx=10, pady=10)

    tk.Label(book_info_frame, text="Title", bg="white").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    tk.Label(book_info_frame, text="Author", bg="white").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    tk.Label(book_info_frame, text="ISBN", bg="white").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    tk.Label(book_info_frame, text="Stock", bg="white").grid(row=3, column=0, padx=10, pady=5, sticky="e")
    tk.Label(book_info_frame, text="Abstract", bg="white").grid(row=4, column=0, padx=10, pady=5, sticky="nw")

    title_value = tk.Label(book_info_frame, bg="white", width=30, relief=tk.SUNKEN)
    title_value.grid(row=0, column=1, padx=10, pady=5, sticky="w")

    author_value = tk.Label(book_info_frame, bg="white", width=30, relief=tk.SUNKEN)
    author_value.grid(row=1, column=1, padx=10, pady=5, sticky="w")

    isbn_value = tk.Label(book_info_frame, bg="white", width=30, relief=tk.SUNKEN)
    isbn_value.grid(row=2, column=1, padx=10, pady=5, sticky="w")

    stock_value = tk.Label(book_info_frame, bg="white", width=30, relief=tk.SUNKEN)
    stock_value.grid(row=3, column=1, padx=10, pady=5, sticky="w")

    abstract_text = tk.Text(book_info_frame, height=5, width=35, wrap="word", relief=tk.SUNKEN, bg="white")
    abstract_text.grid(row=4, column=1, padx=10, pady=5, sticky="w")

    # Navigation Buttons
    nav_frame = tk.Frame(book_info_frame, bg="white")
    nav_frame.grid(row=5, column=1, pady=10, sticky="w")

    prev_button = tk.Button(nav_frame, text="<<", relief=tk.GROOVE, width=3, command=prev_book)
    prev_button.pack(side="left", padx=5)

    next_button = tk.Button(nav_frame, text=">>", relief=tk.GROOVE, width=3, command=next_book)
    next_button.pack(side="left", padx=5)

def search_books(title, author, isbn, category, search_results_treeview):
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
        global rows
        rows = cursor.fetchall()
        if rows:
            search_results_treeview.delete(*search_results_treeview.get_children())  # Clear previous search results
            for row in rows:
                search_results_treeview.insert('', 'end', values=(row[1], row[0]))  # Assuming title and ISBN are in columns 1 and 0
        else:
            messagebox.showinfo("No Results", "No books found matching the criteria.")
    except Exception as e:
        messagebox.showerror("Query Error", f"An error occurred: {e}")
    finally:
        conn.close()

def search_books_action():
    """Wrapper to call search_books with appropriate parameters."""
    global title_entry, author_entry, isbn_entry, category_combobox, search_results_treeview
    
    title = title_entry.get()
    author = author_entry.get()
    isbn = isbn_entry.get()
    category = category_combobox.get()
    
    search_books(title, author, isbn, category, search_results_treeview)

def display_book(index):
    global current_book_index
    if index < 0 or index >= len(rows):
        return

    current_book_index = index
    book = rows[index]
    update_book_info(book)

def update_book_info(book):
    title_value.config(text=book[1])
    author_value.config(text=book[2])
    isbn_value.config(text=book[0])
    stock_value.config(text=str(book[5]))  # Assuming stock is in the 6th column
    abstract_text.delete("1.0", tk.END)
    abstract_text.insert(tk.END, book[4])  # Assuming abstract is in the 5th column

def prev_book():
    if current_book_index > 0:
        display_book(current_book_index - 1)

def next_book():
    if current_book_index < len(rows) - 1:
        display_book(current_book_index + 1)

def on_treeview_select(event):
    """Handle selection in the treeview."""
    selected_item = search_results_treeview.selection()
    if selected_item:
        index = search_results_treeview.index(selected_item[0])
        display_book(index)

# The setup function would be called from your main application when initializing the tab
