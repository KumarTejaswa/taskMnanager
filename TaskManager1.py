import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class TaskManager:
    def __init__(self):
        self.tasks = []
        self.task_id_counter = 1
        self.priority_order = {"high": 1, "medium": 2, "low": 3}
        self.is_completing = False  # Flag to track completion process

    def add_task(self, title, description, due_date=None, priority="medium"):
        task = {
            "id": self.task_id_counter,
            "title": title,
            "description": description,
            "due_date": due_date,
            "priority": priority,
            "completed": False
        }
        self.tasks.append(task)
        self.task_id_counter += 1
        return task["id"]

    def get_incomplete_tasks_sorted(self):
        return sorted(
            [task for task in self.tasks if not task["completed"]],
            key=lambda x: (self.priority_order[x["priority"]], x["id"])
        )

    def complete_task(self, task_id):
        for task in self.tasks:
            if task["id"] == task_id:
                task["completed"] = True
                return True
        return False

    def delete_task(self, task_id):
        for task in self.tasks:
            if task["id"] == task_id:
                self.tasks.remove(task)
                return True
        return False

class TaskManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Manager")
        self.task_manager = TaskManager()
        
        self.root.geometry("800x600")
        self.root.configure(padx=10, pady=10)
        
        self.create_input_frame()
        self.create_task_list_frame()
        
        self.refresh_task_list()

    def create_input_frame(self):
        input_frame = ttk.LabelFrame(self.root, text="Add New Task", padding="10")
        input_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(input_frame, text="Title:").grid(row=0, column=0, sticky="w", pady=2)
        self.title_entry = ttk.Entry(input_frame, width=40)
        self.title_entry.grid(row=0, column=1, columnspan=2, sticky="w", pady=2)

        ttk.Label(input_frame, text="Description:").grid(row=1, column=0, sticky="w", pady=2)
        self.desc_entry = ttk.Entry(input_frame, width=40)
        self.desc_entry.grid(row=1, column=1, columnspan=2, sticky="w", pady=2)

        ttk.Label(input_frame, text="Due Date:").grid(row=2, column=0, sticky="w", pady=2)
        self.date_entry = ttk.Entry(input_frame, width=20)
        self.date_entry.grid(row=2, column=1, sticky="w", pady=2)
        ttk.Label(input_frame, text="(YYYY-MM-DD)").grid(row=2, column=2, sticky="w", pady=2)

        ttk.Label(input_frame, text="Priority:").grid(row=3, column=0, sticky="w", pady=2)
        self.priority_var = tk.StringVar(value="medium")
        priorities = ["high", "medium", "low"]
        self.priority_combo = ttk.Combobox(input_frame, textvariable=self.priority_var, values=priorities, state="readonly")
        self.priority_combo.grid(row=3, column=1, sticky="w", pady=2)

        ttk.Button(input_frame, text="Add Task", command=self.add_task).grid(row=4, column=0, columnspan=3, pady=10)

    def create_task_list_frame(self):
        list_frame = ttk.LabelFrame(self.root, text="Tasks", padding="10")
        list_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Create treeview
        columns = ("ID", "Title", "Description", "Due Date", "Priority", "Status")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # Set column headings and widths
        self.tree.heading("ID", text="ID")
        self.tree.column("ID", width=50)
        self.tree.heading("Title", text="Title")
        self.tree.column("Title", width=150)
        self.tree.heading("Description", text="Description")
        self.tree.column("Description", width=200)
        self.tree.heading("Due Date", text="Due Date")
        self.tree.column("Due Date", width=100)
        self.tree.heading("Priority", text="Priority")
        self.tree.column("Priority", width=80)
        self.tree.heading("Status", text="Status")
        self.tree.column("Status", width=80)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Pack elements
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Buttons frame
        button_frame = ttk.Frame(list_frame)
        button_frame.pack(fill="x", pady=5)

        self.complete_button = ttk.Button(button_frame, text="Complete Tasks Sequentially", command=self.start_sequential_completion)
        self.complete_button.pack(side="left", padx=5)
        
        ttk.Button(button_frame, text="Delete Task", command=self.delete_task).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Refresh", command=self.refresh_task_list).pack(side="left", padx=5)

    def start_sequential_completion(self):
        if self.task_manager.is_completing:
            return
        
        incomplete_tasks = self.task_manager.get_incomplete_tasks_sorted()
        if not incomplete_tasks:
            messagebox.showinfo("Info", "No incomplete tasks remaining!")
            return

        self.task_manager.is_completing = True
        self.complete_button.state(['disabled'])  # Disable button during completion
        self.root.after(0, self.complete_next_task)

    def complete_next_task(self):
        incomplete_tasks = self.task_manager.get_incomplete_tasks_sorted()
        
        if not incomplete_tasks:
            self.task_manager.is_completing = False
            self.complete_button.state(['!disabled'])  # Re-enable button
            messagebox.showinfo("Info", "All tasks completed!")
            return

        # Complete the next task
        next_task = incomplete_tasks[0]
        self.task_manager.complete_task(next_task["id"])
        self.refresh_task_list()

        # Highlight the completed task
        for item in self.tree.get_children():
            if str(self.tree.item(item)['values'][0]) == str(next_task["id"]):
                self.tree.selection_set(item)
                self.tree.see(item)
                break

        # Schedule the next completion after a delay
        self.root.after(1000, self.complete_next_task)  # 1 second delay

    def add_task(self):
        title = self.title_entry.get().strip()
        description = self.desc_entry.get().strip()
        due_date = self.date_entry.get().strip()
        priority = self.priority_var.get()

        if not title:
            messagebox.showerror("Error", "Title is required!")
            return

        if due_date:
            try:
                datetime.strptime(due_date, '%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Error", "Invalid date format! Use YYYY-MM-DD")
                return

        self.task_manager.add_task(title, description, due_date, priority)
        self.refresh_task_list()
        self.clear_inputs()

    def delete_task(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a task to delete!")
            return

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this task?"):
            task_id = int(self.tree.item(selected_item[0])['values'][0])
            if self.task_manager.delete_task(task_id):
                self.refresh_task_list()

    def refresh_task_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Sort tasks by priority and completion status for display
        sorted_tasks = sorted(
            self.task_manager.tasks,
            key=lambda x: (
                x["completed"],
                self.task_manager.priority_order[x["priority"]],
                x["id"]
            )
        )

        for task in sorted_tasks:
            status = "Completed" if task["completed"] else "Pending"
            self.tree.insert("", "end", values=(
                task["id"],
                task["title"],
                task["description"],
                task["due_date"] or "",
                task["priority"],
                status
            ))

    def clear_inputs(self):
        self.title_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.priority_var.set("medium")

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManagerGUI(root)
    root.mainloop()