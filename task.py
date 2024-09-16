from datetime import datetime as dt


class Task:
    def __init__(self, title, content, datetime=None, id=None, created_at=None, status="progress"):
        self.id = id
        self.title = title
        self.content = content
        self.datetime = dt.strptime(datetime, '%Y-%m-%d') if isinstance(datetime, str) else datetime
        self.created_at = created_at or dt.now()
        self.status = status