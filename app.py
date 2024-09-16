import tkinter as tk
from database import Database
from gui import ToDoApp

if __name__ == "__main__":
    root = tk.Tk()
    db = Database()
    app = ToDoApp(root, db)
    app.run()
    db.close()
