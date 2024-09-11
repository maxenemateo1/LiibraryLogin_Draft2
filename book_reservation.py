import tkinter as tk
from tkinter import ttk

def book_reservation_window(search_tab, reservation_tab, username, role):
    """Setup both search and reservation functionalities in the window."""
    setup_search_and_reserve_tab(search_tab)
    setup_reservation_tab(reservation_tab)

def setup_search_and_reserve_tab(tab):
    """Setup the search and reserve tab with book information, filters, and cart."""
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
    tk.Label(book_info_frame, text="--", width=30, relief=tk.SUNKEN).grid(row=1, column=1, padx=10, pady=5, sticky="w")
    tk.Label(book_info_frame, text="--", width=30, relief=tk.SUNKEN).grid(row=2, column=1, padx=10, pady=5, sticky="w")
    tk.Label(book_info_frame, text="--", width=30, relief=tk.SUNKEN).grid(row=3, column=1, padx=10, pady=5, sticky="w")
    tk.Label(book_info_frame, text="--", width=30, relief=tk.SUNKEN).grid(row=4, column=1, padx=10, pady=5, sticky="w")

    abstract_text = tk.Text(book_info_frame, height=5, width=30, wrap="word", relief=tk.SUNKEN)
    abstract_text.grid(row=5, column=1, padx=10, pady=5, sticky="w")

    # Navigation Buttons
    nav_frame = tk.Frame(book_info_frame)
    nav_frame.grid(row=6, column=1, pady=10, sticky="w")

    tk.Button(nav_frame, text="<<", relief=tk.GROOVE, width=3).pack(side="left", padx=5)
    tk.Button(nav_frame, text=">>", relief=tk.GROOVE, width=3).pack(side="left", padx=5)

    # Filter Section: Right Side
    filter_frame = tk.Frame(content_frame, relief=tk.GROOVE, borderwidth=2)
    filter_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

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

    # Author Filter
    tk.Label(filter_frame, text="Author").pack(anchor="w", padx=10)
    author_entry = tk.Entry(filter_frame)
    author_entry.pack(anchor="w", padx=10, pady=5)

    # ISBN Filter
    tk.Label(filter_frame, text="ISBN").pack(anchor="w", padx=10)
    isbn_entry = tk.Entry(filter_frame)
    isbn_entry.pack(anchor="w", padx=10, pady=5)

    # Search Button
    tk.Button(filter_frame, text="Search", relief=tk.GROOVE).pack(pady=10, padx=10)

    # Cart Section
    cart_frame = tk.Frame(content_frame, relief=tk.GROOVE, borderwidth=2)
    cart_frame.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)

    tk.Label(cart_frame, text="Cart", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=5)

    # Cart Table
    cart_tree = ttk.Treeview(cart_frame, columns=("title", "isbn"), show="headings", selectmode="none")
    cart_tree.heading("title", text="Title")
    cart_tree.heading("isbn", text="ISBN")
    cart_tree.pack(padx=10, pady=5)

    # Buttons for Cart
    button_frame = tk.Frame(cart_frame)
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Remove", relief=tk.GROOVE).pack(side="left", padx=5)
    tk.Button(button_frame, text="Reserve", relief=tk.GROOVE).pack(side="left", padx=5)

def setup_reservation_tab(tab):
    """Setup the reservation tab."""
    tk.Label(tab, text="Reservation", font=("Arial", 12, "bold")).pack(pady=20)
    # Placeholder for reservation functionality
    tk.Label(tab, text="Reservation features will be implemented here.").pack(pady=10)
