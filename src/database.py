import csv
import os
from datetime import datetime
from typing import List, Dict, Optional


class TaskDatabase:
    def __init__(self, filename: str = "tasks.csv"):
        self.filename = filename
        self.headers = ["Index", "Todo Item", "Start Date", "In Progress Date", "Completed Date", "Status"]
        self._initialize_csv()
    
    def _initialize_csv(self):
        """Create CSV file with headers if it doesn't exist."""
        if not os.path.exists(self.filename):
            with open(self.filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(self.headers)
    
    def _get_next_index(self) -> int:
        """Get the next available index."""
        tasks = self.load_all_tasks()
        if not tasks:
            return 1
        return max(int(task['Index']) for task in tasks) + 1
    
    def add_task(self, todo_item: str, category: str = "Later") -> Dict:
        """Add a new task with creation timestamp."""
        task = {
            'Index': self._get_next_index(),
            'Todo Item': todo_item,
            'Start Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'In Progress Date': '',
            'Completed Date': '',
            'Status': category  # "Now" or "Later"
        }
        
        with open(self.filename, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.headers)
            writer.writerow(task)
        
        return task
    
    def load_all_tasks(self) -> List[Dict]:
        """Load all tasks from CSV."""
        if not os.path.exists(self.filename):
            return []
        
        tasks = []
        with open(self.filename, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                tasks.append(row)
        return tasks
    
    def update_task(self, index: int, updates: Dict):
        """Update a specific task by index."""
        tasks = self.load_all_tasks()
        
        for task in tasks:
            if int(task['Index']) == index:
                task.update(updates)
                break
        
        self._save_all_tasks(tasks)
    
    def mark_in_progress(self, index: int):
        """Mark task as in progress with timestamp."""
        self.update_task(index, {
            'In Progress Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'Status': 'Now'
        })
    
    def mark_completed(self, index: int):
        """Mark task as completed with timestamp."""
        self.update_task(index, {
            'Completed Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'Status': 'Completed'
        })
    
    def move_to_category(self, index: int, category: str):
        """Move task between Now and Later."""
        self.update_task(index, {'Status': category})
    
    def delete_task(self, index: int):
        """Delete a task by index."""
        tasks = self.load_all_tasks()
        tasks = [task for task in tasks if int(task['Index']) != index]
        self._save_all_tasks(tasks)
    
    def _save_all_tasks(self, tasks: List[Dict]):
        """Save all tasks back to CSV."""
        with open(self.filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.headers)
            writer.writeheader()
            writer.writerows(tasks)
    
    def get_tasks_by_status(self, status: str) -> List[Dict]:
        """Get all tasks with a specific status."""
        return [task for task in self.load_all_tasks() if task['Status'] == status]