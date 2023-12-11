import tkinter as tk
from tkinter import filedialog, Listbox, simpledialog, messagebox, ttk
import os
import re
import json
import markdown
import pypandoc
from bs4 import BeautifulSoup, Comment
from mdx_math import MathExtension
class FileOrganizer:
    def __init__(self, root):
        self.file_map = {}  # Maps chapter names to file paths
        self.load_file_map()
        self.unsaved_changes = False  # Flag to track unsaved changes
        self.root = root
        self.root.geometry("800x500")  # Improved window size
        self.root.title("Professional File Organizer")  # Set a window title
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Use ttk.Style for better theming
        style = ttk.Style()
        style.configure('TButton', font=('Arial', 10), padding=5)
        style.configure('TLabel', font=('Arial', 10), padding=5)
        
        # Adjust the font size for the Listbox entries here
        listbox_font = ('Arial', 18)  # Increased font size for the Listbox

        # Frame for the listbox and scrollbar
        listbox_frame = ttk.Frame(root)
        listbox_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.listbox = Listbox(listbox_frame, exportselection=0, font=listbox_font)
        self.listbox.pack(side="left", fill="both", expand=True)
        self.update_listbox()  # Call to populate the listbox
        
        scrollbar = ttk.Scrollbar(listbox_frame, orient='vertical', command=self.listbox.yview)
        scrollbar.pack(side="right", fill='y')

        self.listbox.config(yscrollcommand=scrollbar.set)
        self.update_listbox()

        # Bind the listbox to the method that updates its item colors
        self.listbox.bind('<Configure>', self.color_listbox_items)

        # Frame for buttons
        button_frame = ttk.Frame(root)
        button_frame.pack(side="right", fill="both", padx=10, pady=10)

        # Button configurations using ttk
        add_button = ttk.Button(button_frame, text="Add File", command=self.add_file)
        add_button.pack(fill="x", pady=5)

        insert_button = ttk.Button(button_frame, text="Insert File", command=self.insert_file)
        insert_button.pack(fill="x", pady=5)

        remove_button = ttk.Button(button_frame, text="Remove File", command=self.remove_file)
        remove_button.pack(fill="x", pady=5)

        update_button = ttk.Button(button_frame, text="Update Files", command=self.update_files)
        update_button.pack(fill="x", pady=5)

        save_button = ttk.Button(button_frame, text="Save to main.html", command=self.save_to_main)
        save_button.pack(fill="x", pady=5)

        # Drag and drop bindings
        self.listbox.bind('<Button-1>', self.start_drag)
        self.listbox.bind('<B1-Motion>', self.do_drag)
        self.listbox.bind('<ButtonRelease-1>', self.stop_drag)
        self.drag_start_index = None
        self.dragging_item = None
        
    
    def color_listbox_items(self, event=None):
        """Apply a custom background color to each item in the listbox."""
        for i in range(self.listbox.size()):
            self.listbox.itemconfig(i, {'bg': '#f0f0f0'})  # Light gray color

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for chapter_name in self.file_map:
            self.listbox.insert(tk.END, chapter_name)
            # Apply color to each item as it is inserted
            self.color_listbox_items()
        
    def start_drag(self, event):
        self.drag_start_index = self.listbox.nearest(event.y)
        self.dragging_item = self.listbox.get(self.drag_start_index)
        self.listbox.itemconfig(self.drag_start_index, {'bg':'gray'})  # Highlight the dragging item

    def do_drag(self, event):
        if self.drag_start_index is None:
            return
        current_index = self.listbox.nearest(event.y)
        if current_index != self.drag_start_index and self.dragging_item:
            self.listbox.delete(self.drag_start_index)
            self.listbox.insert(current_index, self.dragging_item)
            self.listbox.itemconfig(current_index, {'bg':'gray'})  # Keep the new item highlighted
            self.drag_start_index = current_index

    def stop_drag(self, event):
        if self.drag_start_index is None:
            return
        self.listbox.itemconfig(self.drag_start_index, {'bg':'white'})  # Remove the highlight
        # Update file_map order based on the new listbox order
        new_order = [self.listbox.get(i) for i in range(self.listbox.size())]
        self.file_map = {chapter: self.file_map[chapter] for chapter in new_order}
        self.save_file_map()
        self.save_to_main()
        self.dragging_item = None

        
    def on_close(self):
        if self.unsaved_changes:
            if messagebox.askyesno("Quit", "You have unsaved changes. Are you sure you want to quit?"):
                self.root.destroy()
        else:
            self.root.destroy()
            
    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for chapter_name in self.file_map:
            self.listbox.insert(tk.END, chapter_name)
        

    def load_file_map(self):
        if os.path.exists("file_map.json"):
            with open("file_map.json", "r") as file:
                self.file_map = json.load(file)

    def save_file_map(self):
        with open("file_map.json", "w") as file:
            json.dump(self.file_map, file)

    def prompt_for_chapter_name(self):
        return simpledialog.askstring("Chapter Name", "Enter Chapter Name:")

    def add_file(self):
        filename = filedialog.askopenfilename(filetypes=[("All files", "*.*"), ("HTML files", "*.html"), ("Markdown files", "*.md")])
        if filename:
            chapter_name = self.prompt_for_chapter_name()
            if chapter_name:
                self.file_map[chapter_name] = filename
                self.update_listbox()
                self.save_file_map()
                self.save_to_main()  # Automatically save changes
                messagebox.showinfo("Success", "File added and saved successfully")
    def update_files(self):
        # Iterate over the files and update the content
        for chapter_name in self.file_map:
            file_path = self.file_map[chapter_name]
            with open(file_path, 'r') as file:
                # Read the file content
                file_content = file.read()
                # Here you can add logic to modify file_content if needed

        # After updating, save to main.html
        self.save_to_main()
        messagebox.showinfo("Success", "Files updated and main.html saved successfully")

    def generate_sidebar_links(self, main_file, chapter_name, child_chapters):
        # Combine navigation and collapsible functionality into one element
        main_file.write(f'<div class="collapsible" href="#{chapter_name}" data-toggle="collapse" data-target="#collapse-{chapter_name}">{chapter_name}</div>\n')
        main_file.write(f'<div id="collapse-{chapter_name}" class="collapse">\n')

        for child_name, level in child_chapters.items():
            indent_class = f"level-{level}"
            main_file.write(f'<a class="{indent_class}" href="#{child_name}">{child_name}</a><br>\n')

        main_file.write('</div>\n')




    def insert_file(self):
        filename = filedialog.askopenfilename(filetypes=[ ("HTML files", "*.html"),("Markdown files", "*.md")])
        if filename:
            chapter_name = self.prompt_for_chapter_name()
            if chapter_name:
                index = self.listbox.curselection()[0]
                key_list = list(self.file_map.keys())
                key_list.insert(index, chapter_name)
                self.file_map = {k: self.file_map[k] for k in key_list if k in self.file_map}
                self.file_map[chapter_name] = filename
                self.update_listbox()
                self.save_file_map()
                self.save_to_main()  # Automatically save changes

    def remove_file(self):
        selected_items = self.listbox.curselection()
        if selected_items:
            index = selected_items[0]
            chapter_name = self.listbox.get(index)
            del self.file_map[chapter_name]
            self.update_listbox()
            self.save_file_map()
            self.save_to_main()  # Automatically save changes
            messagebox.showinfo("Success", "File removed and saved successfully")

    def find_child_chapters(self, content):
        """
        Updated to find child chapters along with their levels.
        """
        child_chapters = {}
        lines = content.split("\n")
        for line in lines:
            if "<!-- BREAKPOINT" in line:
                parts = line.split(":", 1)
                level = 2  # Default level
                if "_" in parts[0]:
                    # Extract level if specified
                    level = int(parts[0].split("_")[1].replace("<!-- BREAKPOINT", "").strip())
                child_name = parts[1].strip().rstrip("-->").strip()
                child_chapters[child_name] = level
        return child_chapters
    
    def add_breakpoints_to_content(self, content, breakpoints):
        new_content = []
        for line in content.split('\n'):
            for bp in breakpoints:
                # Regular expression to match the breakpoint comment
                pattern = re.compile(r'<!--\s*BREAKPOINT: ' + re.escape(bp) + r'\s*-->')
                if pattern.search(line):
                    # Replace the comment with an invisible anchor tag
                    invisible_anchor = f'<a id="{bp}" style="display: inline; height: 0; margin: 0; padding: 0;"></a>'
                    line = pattern.sub(invisible_anchor, line)
            new_content.append(line)
        return '\n'.join(new_content)




    def save_to_main(self):
        with open("main.html", "w", encoding='utf-8') as main_file:
            main_file.write("""
            <!DOCTYPE html>
            <html>
            <head>
            <style>
            body {
                margin: 0;
                font-family: Arial, sans-serif;
            }
            a.level-2 {
                padding: 10px 15px;
                text-decoration: none;
                font-size: 14px;
                color: #818181;
                background-color: #f7f7f7;
                display: block;
            }

            .sidebar {
                height: 100%;
                width: 200px;
                position: fixed;
                z-index: 1;
                top: 0;
                left: 0;
                background-color: #111;
                overflow-x: hidden;
                padding-top: 20px;
            }

            .sidebar a {
                padding: 10px 15px;
                text-decoration: none;
                font-size: 18px;
                color: #818181;
                display: block;
            }

            .sidebar a:hover {
                background-color: #575757; /* Lighter color on hover */
                color: #f1f1f1;
            }

            .sidebar a.active {
                background-color: #ffffff; /* White color on active/click */
                color: #000000;
            }
            .collapsible {
                padding: 10px 15px;
                text-decoration: none;
                font-size: 18px;
                color: #818181;
                display: block;
            }

            .collapsible:hover {
                background-color: #575757; /* Lighter color on hover */
                color: #f1f1f1;
            }

            .collapsible.active {
                background-color: #ffffff; /* White color on active/click */
                color: #000000;
            }

            .main-content {
                margin-left: 200px;
                padding: 0px 10px;
            }

            .hidden {
                display: none;
            }
        </style>
            <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
            <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
            <script type="text/javascript" async
                src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_CHTML">
            </script>
            <script>
            
            document.addEventListener('DOMContentLoaded', function() {
                document.querySelectorAll('.collapsible').forEach(function(collapsible) {
                    collapsible.addEventListener('click', function() {
                        var targetId = this.getAttribute('href');
                        var targetCollapse = this.getAttribute('data-target');

                        // Navigate to the chapter head
                        document.querySelector(targetId).scrollIntoView({ behavior: 'smooth' });

                        // Toggle the visibility of child items
                        var content = document.querySelector(targetCollapse);
                        content.classList.toggle('collapse');
                    });
                });
            });
            </script>
            </head>
            <body>
            <div class="sidebar">
        """)

            # Sidebar links
            for chapter_name in self.file_map:
                # main_file.write(f'<a href="#{chapter_name}">{chapter_name}</a>\n')
                file_path = self.file_map[chapter_name]
                with open(file_path, "r", encoding='utf-8') as f:  # Ensure UTF-8 encoding for reading
                    if file_path.endswith('.md'):
                        # Convert Markdown to HTML
                        file_content = markdown.markdown(f.read())
                    else:
                        file_content = f.read()

                    child_chapters = self.find_child_chapters(file_content)
                    self.generate_sidebar_links(main_file, chapter_name, child_chapters)
            main_file.write("""
                <script>
                    function toggleVisibility(chapterName, level) {
                        // Select all direct children links of the clicked chapter
                        var childLinks = document.querySelectorAll(`.child-of-${chapterName}.level-${level + 1}`);

                        childLinks.forEach(function(link) {
                            // Toggle the 'hidden' class to show or hide the element
                            link.classList.toggle('hidden');
                        });
                    }
                </script>
                """)
            main_file.write("""
            </div>
            <div class='main-content'>
        """)

            # Main content
            for chapter_name, file_path in self.file_map.items():
                with open(file_path, "r", encoding='utf-8') as f:
                    if file_path.endswith('.md'):
                        file_content = markdown.markdown(f.read(), extensions=[MathExtension()])
                    else:
                        # Remove style tags from HTML content
                        soup = BeautifulSoup(f.read(), 'html.parser')
                        for style_tag in soup.find_all('style'):
                            style_tag.decompose()
                        file_content = str(soup)
                    child_chapters = self.find_child_chapters(file_content)
                    # for child_name in child_chapters:
                    #     # Here, create sidebar links for each child chapter
                    #     main_file.write(f'<a href="#{child_name}">{child_name}</a>\n')
                    main_file.write(f'<div id="{chapter_name}">\n')
                    file_content_with_breakpoints = self.add_breakpoints_to_content(file_content, child_chapters)
                    main_file.write(file_content_with_breakpoints)
                    main_file.write('</div>\n')
                    

            main_file.write("""
                </div>
                </body>
                </html>
            """)

# Create the main window
root = tk.Tk()
root.title("File Organizer")

app = FileOrganizer(root)

root.mainloop()