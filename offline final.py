import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
import requests
import shutil
import json

# Create a folder for storing books
BOOK_FOLDER = "books"
os.makedirs(BOOK_FOLDER, exist_ok=True)

# Sample categories
CATEGORIES = ["Science", "Technology", "Mathematics", "Literature", "Others"]

# In-memory library data
library = []
online_search_results = []

LIBRARY_FILE = "library.json"

def load_library():
    global library
    if os.path.exists(LIBRARY_FILE):
        with open(LIBRARY_FILE, "r", encoding="utf-8") as f:
            library = json.load(f)
    else:
        library = []

def save_library():
    with open(LIBRARY_FILE, "w", encoding="utf-8") as f:
        json.dump(library, f, indent=2)

def search_books_online():
    """Search for books online using Open Library API"""
    search_term = search_entry.get().strip()
    if not search_term:
        messagebox.showwarning("Warning", "Please enter a search term!")
        return
    
    try:
        # Show loading message
        status_label.config(text="🔍 Searching online...", fg='#3498db')
        root.update()
        
        # Search using Open Library API
        url = f"https://openlibrary.org/search.json?title={search_term}&limit=20"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            global online_search_results
            online_search_results = []
            
            if 'docs' in data and data['docs']:
                for book in data['docs']:
                    title = book.get('title', 'Unknown Title')
                    author = ', '.join(book.get('author_name', ['Unknown Author']))
                    first_publish_year = book.get('first_publish_year', 'Unknown Year')
                    
                    # Try to get download link (this is simplified - real implementation would need more work)
                    download_url = None
                    if 'ia' in book:  # Internet Archive ID
                        download_url = f"https://archive.org/download/{book['ia'][0]}/{book['ia'][0]}.pdf"
                    
                    online_search_results.append({
                        'title': title,
                        'author': author,
                        'year': first_publish_year,
                        'download_url': download_url
                    })
                
                # Update the online results display
                update_online_results()
                status_label.config(text=f"✅ Found {len(online_search_results)} books online", fg='#27ae60')
            else:
                status_label.config(text="❌ No books found online", fg='#e74c3c')
                online_book_list.delete(0, tk.END)
        else:
            status_label.config(text="❌ Error connecting to online library", fg='#e74c3c')
            
    except requests.RequestException:
        status_label.config(text="❌ No internet connection or server error", fg='#e74c3c')
    except Exception as e:
        status_label.config(text="❌ An error occurred during search", fg='#e74c3c')

def update_online_results():
    """Update the online search results listbox"""
    online_book_list.delete(0, tk.END)
    for book in online_search_results:
        display_text = f"{book['title']} - {book['author']} ({book['year']})"
        online_book_list.insert(tk.END, display_text)

def download_selected_book():
    """Download the selected book from online search results"""
    selected = online_book_list.curselection()
    if not selected:
        messagebox.showwarning("Warning", "Please select a book to download!")
        return
    
    book = online_search_results[selected[0]]
    
    if not book['download_url']:
        messagebox.showinfo("Info", "Direct download not available for this book. You can try searching for it manually.")
        return
    
    try:
        # Ask user for category
        category = simpledialog.askstring("Category", f"Enter category ({', '.join(CATEGORIES)}):", initialvalue="Others")
        if not category:
            category = "Others"
        
        status_label.config(text="📥 Downloading book...", fg='#3498db')
        root.update()
        
        # Download the book
        response = requests.get(book['download_url'], timeout=30)
        if response.status_code == 200:
            # Save the book
            safe_title = "".join(c for c in book['title'] if c.isalnum() or c in (' ', '-', '_')).strip()
            dest_path = os.path.join(BOOK_FOLDER, f"{safe_title}.pdf")
            
            with open(dest_path, 'wb') as f:
                f.write(response.content)
            
            # Add to library
            library.append({
                "title": book['title'],
                "path": dest_path,
                "category": category,
                "author": book['author']
            })
            save_library()
            update_list()
            status_label.config(text="✅ Book downloaded successfully!", fg='#27ae60')
            messagebox.showinfo("Success", f"Book '{book['title']}' downloaded and added to your library!")
        else:
            status_label.config(text="❌ Failed to download book", fg='#e74c3c')
            
    except Exception as e:
        status_label.config(text="❌ Error downloading book", fg='#e74c3c')
        messagebox.showerror("Error", f"Failed to download book: {str(e)}")

def download_book():
    title = title_entry.get()
    category = category_cb.get()
    # Add your download implementation here
    pass

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
        save_library()
        update_list()
        messagebox.showinfo("Success", f"Book '{title}' added to your library.")

def search_books():
    """Search for books based on title and category filter"""
    update_list()

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
        path = library[index]['path']
        if os.name == 'nt':  # Windows
            os.startfile(path)
        else:  # Linux/Mac
            os.system(f"xdg-open '{path}'")

def clear_search():
    """Clear search field and show all books"""
    search_entry.delete(0, tk.END)
    category_filter_cb.set("All")
    update_list()

# GUI setup
root = tk.Tk()
root.title("Community Offline Library")
root.geometry("800x600")
root.configure(bg='#f0f0f0')

# Main container
main_frame = tk.Frame(root, bg='#f0f0f0')
main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

# Title
title_label = tk.Label(main_frame, text="📚 Community Offline Library", 
                      font=('Arial', 18, 'bold'), bg='#f0f0f0', fg='#2c3e50')
title_label.pack(pady=(0, 20))

# Add Book Section
add_frame = tk.LabelFrame(main_frame, text="Add New Book", font=('Arial', 12, 'bold'), 
                         bg='#f0f0f0', fg='#34495e', padx=10, pady=10)
add_frame.pack(fill=tk.X, pady=(0, 20))

# Book title entry frame
title_frame = tk.Frame(add_frame, bg='#f0f0f0')
title_frame.pack(fill=tk.X, pady=5)

tk.Label(title_frame, text="Book Title:", font=('Arial', 10), bg='#f0f0f0').pack(side=tk.LEFT)
title_entry = tk.Entry(title_frame, width=40, font=('Arial', 10))
title_entry.pack(side=tk.LEFT, padx=(10, 0))

# Category selection frame
category_frame = tk.Frame(add_frame, bg='#f0f0f0')
category_frame.pack(fill=tk.X, pady=5)

tk.Label(category_frame, text="Category:", font=('Arial', 10), bg='#f0f0f0').pack(side=tk.LEFT)
category_cb = ttk.Combobox(category_frame, values=CATEGORIES, state="readonly", width=20)
category_cb.set("Science")
category_cb.pack(side=tk.LEFT, padx=(10, 0))

# Add book button
add_btn_frame = tk.Frame(add_frame, bg='#f0f0f0')
add_btn_frame.pack(fill=tk.X, pady=10)

tk.Button(add_btn_frame, text="📁 Add Book From Device", command=add_local_book,
          font=('Arial', 10, 'bold'), bg='#3498db', fg='white', 
          padx=20, pady=5, cursor='hand2').pack(side=tk.LEFT)

# Search Section
search_frame = tk.LabelFrame(main_frame, text="Search & Filter", font=('Arial', 12, 'bold'),
                            bg='#f0f0f0', fg='#34495e', padx=10, pady=10)
search_frame.pack(fill=tk.X, pady=(0, 20))

# Search controls frame
search_controls = tk.Frame(search_frame, bg='#f0f0f0')
search_controls.pack(fill=tk.X)

# Search by title
tk.Label(search_controls, text="Search Title:", font=('Arial', 10), bg='#f0f0f0').grid(row=0, column=0, sticky='w', padx=(0, 5))
search_entry = tk.Entry(search_controls, width=30, font=('Arial', 10))
search_entry.grid(row=0, column=1, padx=5)

# Search button
tk.Button(search_controls, text="🔍 Search Online", command=search_books_online,
          font=('Arial', 9, 'bold'), bg='#27ae60', fg='white',
          padx=15, pady=2, cursor='hand2').grid(row=0, column=2, padx=5)

# Local search button
tk.Button(search_controls, text="📚 Search Library", command=search_books,
          font=('Arial', 9, 'bold'), bg='#3498db', fg='white',
          padx=15, pady=2, cursor='hand2').grid(row=0, column=3, padx=5)

# Category filter
tk.Label(search_controls, text="Filter by Category:", font=('Arial', 10), bg='#f0f0f0').grid(row=0, column=4, sticky='w', padx=(20, 5))
category_filter_cb = ttk.Combobox(search_controls, values=["All"] + CATEGORIES, state="readonly", width=15)
category_filter_cb.set("All")
category_filter_cb.grid(row=0, column=5, padx=5)
category_filter_cb.bind("<<ComboboxSelected>>", lambda e: update_list())

# Clear button
tk.Button(search_controls, text="🗑️ Clear", command=clear_search,
          font=('Arial', 9, 'bold'), bg='#e74c3c', fg='white',
          padx=15, pady=2, cursor='hand2').grid(row=0, column=6, padx=5)

# Status label for search feedback
status_label = tk.Label(search_frame, text="Ready to search...", 
                       font=('Arial', 9), bg='#f0f0f0', fg='#7f8c8d')
status_label.pack(pady=(10, 0))

# Online Search Results Section
online_frame = tk.LabelFrame(main_frame, text="Online Search Results", font=('Arial', 12, 'bold'),
                            bg='#f0f0f0', fg='#34495e', padx=10, pady=10)
online_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

# Online books list container
online_container = tk.Frame(online_frame, bg='#f0f0f0')
online_container.pack(fill=tk.BOTH, expand=True)

# Online books scrollbar
online_scrollbar = tk.Scrollbar(online_container)
online_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Online books listbox
online_book_list = tk.Listbox(online_container, font=('Arial', 10), 
                             yscrollcommand=online_scrollbar.set, selectbackground='#e67e22',
                             bg='#ecf0f1', fg='#2c3e50', selectforeground='white', height=6)
online_book_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
online_scrollbar.config(command=online_book_list.yview)

# Download button for online books
download_btn_frame = tk.Frame(online_frame, bg='#f0f0f0')
download_btn_frame.pack(fill=tk.X, pady=(10, 0))

tk.Button(download_btn_frame, text="📥 Download Selected Book", command=download_selected_book,
          font=('Arial', 10, 'bold'), bg='#e67e22', fg='white', 
          padx=20, pady=5, cursor='hand2').pack(side=tk.LEFT)

# Books List Section
list_frame = tk.LabelFrame(main_frame, text="Your Library", font=('Arial', 12, 'bold'),
                          bg='#f0f0f0', fg='#34495e', padx=10, pady=10)
list_frame.pack(fill=tk.BOTH, expand=True)

# Scrollable book list
list_container = tk.Frame(list_frame, bg='#f0f0f0')
list_container.pack(fill=tk.BOTH, expand=True)

# Scrollbar
scrollbar = tk.Scrollbar(list_container)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Book listbox
book_list = tk.Listbox(list_container, font=('Arial', 10), 
                      yscrollcommand=scrollbar.set, selectbackground='#3498db',
                      bg='white', fg='#2c3e50', selectforeground='white')
book_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.config(command=book_list.yview)

# Bind double click to open book
book_list.bind("<Double-Button-1>", open_book)

# Instructions
instructions = tk.Label(main_frame, text="💡 Double-click on a book to open it", 
                       font=('Arial', 9, 'italic'), bg='#f0f0f0', fg='#7f8c8d')
instructions.pack(pady=(10, 0))

# Bind Enter key to search
search_entry.bind('<Return>', lambda e: search_books_online())

# Load library at startup
load_library()

# Initialize the list
update_list()

root.mainloop()
