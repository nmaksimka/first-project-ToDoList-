import sqlite3
from datetime import datetime as dt
from task import Task


class Database:
    def __init__(self, db_name="tasks.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT,
            datetime TEXT,
            created_at TEXT NOT NULL,
            status TEXT NOT NULL
        )
        """
        self.conn.execute(query)
        self.conn.commit()

    def add_task(self, task):
        query = """
        INSERT INTO tasks (title, content, datetime, created_at, status)
        VALUES (?, ?, ?, ?, ?)
        """
        self.conn.execute(query, (
            task.title, task.content, task.datetime.strftime('%Y-%m-%d') if task.datetime else None,
            task.created_at.strftime('%Y-%m-%d %H:%M:%S'), task.status))
        self.conn.commit()

    def get_tasks(self, status=None):
        if status:
            query = "SELECT * FROM tasks WHERE status = ?"
            rows = self.conn.execute(query, (status,)).fetchall()
        else:
            query = "SELECT * FROM tasks"
            rows = self.conn.execute(query).fetchall()
        tasks = [Task(row[1], row[2], row[3], row[0], row[4], row[5]) for row in rows]
        return tasks

    def update_task(self, task):
        query = """
        UPDATE tasks
        SET title = ?, content = ?, datetime = ?, status = ?
        WHERE id = ?
        """
        self.conn.execute(query, (
            task.title, task.content, task.datetime.strftime('%Y-%m-%d') if task.datetime else None, task.status,
            task.id))
        self.conn.commit()

    def delete_task(self, task_id):
        query = "DELETE FROM tasks WHERE id = ?"
        self.conn.execute(query, (task_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()