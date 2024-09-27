import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from task import Task
from datetime import datetime as dt, datetime


class ToDoApp:
    def __init__(self, root, db):
        self.filter_combobox = None
        self.date_entry_button = None
        self.done_task_tree = None
        self.search_entry = None
        self.task_tree = None
        self.root = root
        self.db = db
        self.root.title("To-Do List")
        self.root.resizable(False, False)
        self.create_widgets()
        self.update_task_list()

    def create_widgets(self):
        top_frame = tk.Frame(self.root)
        top_frame.grid(row=0, column=0, pady=10, sticky="ew")

        self.search_entry = tk.Entry(top_frame)
        self.search_entry.grid(row=0, column=0, padx=5, sticky="w")
        search_button = tk.Button(top_frame, text="Update Search", bg="lightgray", command=self.search_tasks)
        search_button.grid(row=0, column=1, padx=5, sticky="ew")

        self.filter_combobox = ttk.Combobox(top_frame, values=["All", "In Progress", "Expired", "Done"])
        self.filter_combobox.set("All")
        self.filter_combobox.grid(row=0, column=2, padx=5, sticky="ew")
        self.filter_combobox.bind("<<ComboboxSelected>>", self.filter_tasks)

        task_tree_frame = tk.Frame(self.root)
        task_tree_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        task_tree_frame.grid_rowconfigure(0, weight=1)
        task_tree_frame.grid_columnconfigure(0, weight=1)

        self.task_tree = ttk.Treeview(task_tree_frame, columns=("ID", "Title", "Due Date", "Status"), show="headings")
        self.task_tree.heading("ID", text="ID")
        self.task_tree.heading("Title", text="Title")
        self.task_tree.heading("Due Date", text="Due Date")
        self.task_tree.heading("Status", text="Status")
        self.task_tree.grid(row=0, column=0, sticky="nsew")

        task_tree_scrollbar = tk.Scrollbar(task_tree_frame, orient="vertical", command=self.task_tree.yview)
        task_tree_scrollbar.grid(row=0, column=1, sticky="ns")

        self.task_tree.configure(yscrollcommand=task_tree_scrollbar.set)

        self.task_tree.bind("<Double-1>", self.on_item_double_click)

        bottom_frame = tk.Frame(self.root)
        bottom_frame.grid(row=2, column=0, pady=10, sticky="ew")

        add_button = tk.Button(bottom_frame, text="Add Task", bg="lightgray", command=self.add_task)
        add_button.pack(side=tk.LEFT, padx=10, pady=10)

    def update_task_list(self, tasks=None):
        for row in self.task_tree.get_children():
            self.task_tree.delete(row)
        tasks = tasks or self.db.get_tasks(status=None)
        for task in tasks:
            self.task_tree.insert("", "end", values=(
                task.id, task.title, task.datetime.strftime('%Y-%m-%d') if task.datetime else "No Deadline",
                task.status))

    def search_tasks(self):
        query = self.search_entry.get()
        filter_value = self.filter_combobox.get()
        status_mapping = {
            "All": None,
            "In Progress": "progress",
            "Expired": "expired",
            "Done": "done"
        }
        status = status_mapping.get(filter_value)
        tasks = self.db.get_tasks(status=status)
        filtered_tasks = [task for task in tasks if
                          query.lower() in task.title.lower() or query.lower() in task.content.lower()]
        self.update_task_list(filtered_tasks)

    def on_item_double_click(self, event):
        selected_items = self.task_tree.selection()
        if not selected_items:
            return

        selected_item = selected_items[0]
        task_id = self.task_tree.item(selected_item)["values"][0]
        task = next(task for task in self.db.get_tasks() if task.id == task_id)
        self.view_task(task)

    def add_task(self):
        self.edit_task()

    def save_new_task(self, title, content, due_date, window):
        new_task = Task(
            title=title,
            content=content,
            datetime=due_date if due_date else None,
        )
        if due_date is None or due_date >= dt.today().date():
            new_task.status = "progress"
        else:
            new_task.status = "expired"
        self.db.add_task(new_task)
        self.update_task_list()
        window.destroy()

    def view_task(self, task):
        view_task_window = tk.Toplevel(self.root)
        view_task_window.title("View Task")
        view_task_window.resizable(False, False)

        tk.Label(view_task_window, text="Title").grid(row=0, column=0, pady=5, padx=5)
        title_entry = tk.Entry(view_task_window)
        title_entry.insert(0, task.title)
        title_entry.grid(row=0, column=1, pady=5, padx=5)
        title_entry.config(state="readonly")

        tk.Label(view_task_window, text="Content").grid(row=1, column=0, pady=5, padx=5)
        content_text = tk.Text(view_task_window, height=10, width=40)
        content_text.insert("1.0", task.content)
        content_text.grid(row=1, column=1, pady=5, padx=5)
        content_text.config(state="disabled")

        if task.status == "expired":
            tk.Label(view_task_window, text="Expired", fg="red").grid(row=2, column=1, pady=5, padx=5, sticky="sw")
        elif task.status == "done" and task.status != "expired":
            tk.Label(view_task_window, text="Done", fg="green").grid(row=2, column=1, pady=5, padx=5, sticky="sw")
        else:
            tk.Label(view_task_window, text="Progress", fg="gray").grid(row=2, column=1, pady=5, padx=5, sticky="sw")

        if task.datetime:
            deadline_label = tk.Label(view_task_window, text=f"Due Date: {task.datetime.strftime('%Y-%m-%d')}")
            deadline_label.grid(row=3, column=1, pady=5, padx=5)

        edit_button = tk.Button(view_task_window, text="Edit",bg="lightgray", command=lambda: self.edit_task(task, view_task_window))
        edit_button.grid(row=4, column=1, pady=15, padx=15, sticky="se")

        if task.status != "done" and task.status != "expired":
            done_button = tk.Button(view_task_window, text="Done", fg="green",
                                    command=lambda: (self.mark_task_as_done(task.id), view_task_window.destroy()))
            done_button.grid(row=4, pady=15, padx=15, sticky="se")

    def edit_task(self, task=None, view_task_window=None):
        if view_task_window:
            view_task_window.destroy()

        edit_task_window = tk.Toplevel(self.root)
        edit_task_window.title("Edit Task" if task else "Add Task")
        edit_task_window.resizable(False, False)

        tk.Label(edit_task_window, text="Title").grid(row=0, column=0, pady=0, padx=0)
        title_entry = tk.Entry(edit_task_window, width=40)
        title_entry.grid(row=0, column=1, pady=5, padx=5)

        tk.Label(edit_task_window, text="Content").grid(row=1, column=0, pady=5, padx=5)
        content_text = tk.Text(edit_task_window, height=10, width=40)
        content_text.grid(row=1, column=1, pady=5, padx=5)

        if task:
            if task.status == "expired":
                tk.Label(edit_task_window, text="Expired", fg="red").grid(row=2, column=1, pady=5, padx=5, sticky="sw")
            elif task.status == "done":
                tk.Label(edit_task_window, text="Done", fg="green").grid(row=2, column=1, pady=5, padx=5, sticky="sw")
            else:
                tk.Label(edit_task_window, text="Progress", fg="gray").grid(row=2, column=1, pady=5, padx=5, sticky="sw")

            title_entry.insert(0, task.title)
            content_text.insert("1.0", task.content)

        tk.Label(edit_task_window, text="Due Date").grid(row=3, column=0, pady=5, padx=5)
        date_entry = DateEntry(edit_task_window, state="readonly")
        date_entry.grid(row=3, column=1, pady=5, padx=5)
        if task and task.datetime:
            date_entry.set_date(task.datetime)

        button_frame = tk.Frame(edit_task_window)
        button_frame.grid(row=4, column=1, pady=10)

        save_button = tk.Button(button_frame, text="Save", bg="lightgreen", command=lambda: self.save_task(task, title_entry.get(),
                                                                                          content_text.get("1.0",
                                                                                                           tk.END).strip(),
                                                                                          date_entry.get_date(),
                                                                                          edit_task_window))
        save_button.grid(row=1, column=2, sticky="se", padx=20)

        cancel_button = tk.Button(button_frame, text="Cancel", bg="pink", command=edit_task_window.destroy)
        cancel_button.grid(row=1, column=1, sticky="s", padx=20)

        if task:
            delete_button = tk.Button(button_frame, text="Delete", bg="red", command=lambda: self.delete_task(task.id, edit_task_window))
            delete_button.grid(row=1, column=0, sticky="sw", padx=20)

    def delete_task(self, task_id, window = None):
        confirm = messagebox.askyesno("Warning", "Are you sure, you want to delete this task?")

        if confirm:
            self.db.delete_task(task_id)
            self.update_task_list()

        if window:
            window.destroy()

    def mark_task_as_done(self, task_id):
        task = next(task for task in self.db.get_tasks() if task.id == task_id)
        task.status = "done"
        self.db.update_task(task)
        self.update_task_list()

    def save_task(self, task, title, content, due_date, window):
        if due_date < dt.today().date() and task.status != "progress":
            messagebox.showerror("Error", "You cannot select a date earlier than today!")
            return
        if not title.strip():
            messagebox.showerror("Error", "Task title cannot be empty!")
            return
        if not content.strip():
            messagebox.showerror("Error", "Task content cannot be empty!")
            return

        if task is None:
            self.save_new_task(title, content, due_date, window)
            return

        task.title = title
        task.content = content
        task.datetime = due_date
        if due_date is None or due_date >= dt.today().date():
            task.status = "progress"
        else:
            task.status = "expired"
        self.db.update_task(task)
        self.update_task_list()
        window.destroy()

    def run(self):
        self.root.mainloop()

    def filter_tasks(self, event=None):
        filter_value = self.filter_combobox.get()
        status_mapping = {
            "All": None,
            "In Progress": "progress",
            "Expired": "expired",
            "Done": "done"
        }
        status = status_mapping.get(filter_value)
        tasks = self.db.get_tasks(status=status)
        self.update_task_list(tasks)