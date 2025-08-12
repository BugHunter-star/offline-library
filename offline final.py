import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
import requests
import shutil

# Create a folder for storing books
BOOK_FOLDER = "books"
os.makedirs(BOOK_FOLDER, exist_ok=True)

# Sample categories
CATEGORIES = ["Science", "Technology", "Mathematics", "Literature", "Others"]

# In-memory library data
library = []

def download_book():

    title = title_entry.get()
    category = category_cb.get()

def add_local_book():
    filepath = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if not filepath:
        return
    title = simpledialog.askstring("Book Title", "Enter the book title:")
    category = simpledialog.askstring("Category", f"Enter category ({', '.join(CATEGORIES)}):", initialvalue="Others")

    if title:
        dest_path = os.path.join(BOOK_FOLDER, f"{title}.pdf")
        shutil.copy(filepath, dest_path)
        library.append({"title": title, "path": dest_path, "category": category})
        update_list()
        messagebox.showinfo("Success", f"Book '{title}' added to your library.")

def update_list():
    search_term = search_entry.get().lower()
    category_filter = category_filter_cb.get()

    book_list.delete(0, tk.END)
    for book in library:
        if search_term in book["title"].lower() and (category_filter == "All" or book["category"] == category_filter):
            book_list.insert(tk.END, f"{book['title']} ({book['category']})")

def open_book(event):
    selected = book_list.curselection()
    if selected:
        index = selected[0]
        os.system(f"xdg-open '{library[index]['path']}'")

# GUI setup
root = tk.Tk()
root.title("Community Offline Library")
root.geometry("700x500")

frame = tk.Frame(root)
frame.pack(pady=10)

# URL download section
tk.Label(frame, text="Book Title:").grid(row=0, column=0)
title_entry = tk.Entry(frame, width=30)
title_entry.grid(row=0, column=1)

category_cb = ttk.Combobox(frame, values=CATEGORIES, state="readonly")
category_cb.set("Science")
category_cb.grid(row=0, column=2, padx=10)
# Add local book
tk.Button(root, text="Add Book From Device", command=add_local_book).pack(pady=5)

# Search and filter
search_frame = tk.Frame(root)
search_frame.pack()

tk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
search_entry = tk.Entry(search_frame)
search_entry.pack(side=tk.LEFT)
search_entry.bind("<KeyRelease>", lambda e: update_list())

category_filter_cb = ttk.Combobox(search_frame, values=["All"] + CATEGORIES, state="readonly")
category_filter_cb.set("All")
category_filter_cb.pack(side=tk.LEFT)
category_filter_cb.bind("<<ComboboxSelected>>", lambda e: update_list())

# Book list
book_list = tk.Listbox(root, width=80, height=20)
book_list.pack(pady=10)
book_list.bind("<Double-Button-1>", open_book)

root.mainloop()
