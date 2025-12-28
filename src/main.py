import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QLineEdit, 
                             QScrollArea, QCheckBox, QMessageBox)
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QFont
from database import TaskDatabase


class TaskWidget(QWidget):
    """Individual task item widget."""
    def __init__(self, task_data, parent_window):
        super().__init__()
        self.task_data = task_data
        self.parent_window = parent_window
        self.setObjectName("taskItem")
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Checkbox for completion
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(bool(self.task_data['Completed Date']))
        self.checkbox.stateChanged.connect(self.toggle_completion)
        layout.addWidget(self.checkbox)
        
        # Task text
        self.task_label = QLabel(self.task_data['Todo Item'])
        self.task_label.setObjectName("taskText" if not self.task_data['Completed Date'] else "completedTask")
        self.task_label.setWordWrap(True)
        layout.addWidget(self.task_label, stretch=1)
        
        # Start button (only if not in progress and not completed)
        if not self.task_data['In Progress Date'] and not self.task_data['Completed Date']:
            self.start_btn = QPushButton("▶")
            self.start_btn.setObjectName("smallBtn")
            self.start_btn.setToolTip("Start working on this")
            self.start_btn.clicked.connect(self.mark_in_progress)
            layout.addWidget(self.start_btn)
        
        # Delete button
        self.delete_btn = QPushButton("✕")
        self.delete_btn.setObjectName("smallBtn")
        self.delete_btn.setToolTip("Delete task")
        self.delete_btn.clicked.connect(self.delete_task)
        layout.addWidget(self.delete_btn)
        
        self.setLayout(layout)
    
    def toggle_completion(self, state):
        """Toggle task completion status."""
        task_index = int(self.task_data['Index'])
        if state == Qt.Checked:
            self.parent_window.db.mark_completed(task_index)
        else:
            self.parent_window.db.update_task(task_index, {'Completed Date': ''})
        self.parent_window.refresh_tasks()
    
    def mark_in_progress(self):
        """Mark task as in progress."""
        task_index = int(self.task_data['Index'])
        self.parent_window.db.mark_in_progress(task_index)
        self.parent_window.refresh_tasks()
    
    def delete_task(self):
        """Delete this task."""
        task_index = int(self.task_data['Index'])
        self.parent_window.db.delete_task(task_index)
        self.parent_window.refresh_tasks()


class StickyNoteApp(QMainWindow):
    """Main application window."""
    def __init__(self):
        super().__init__()
        self.db = TaskDatabase()
        self.dragging = False
        self.offset = QPoint()
        
        self.setup_window()
        self.setup_ui()
        self.setup_reminder_timer()
        self.refresh_tasks()
    
    def setup_window(self):
        """Configure main window properties."""
        self.setWindowTitle("📌 Stick To It")
        self.setFixedWidth(350)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        
        # Load stylesheet
        style_path = os.path.join(os.path.dirname(__file__), 'styles.qss')
        if os.path.exists(style_path):
            with open(style_path, 'r') as f:
                self.setStyleSheet(f.read())
    
    def setup_ui(self):
        """Create the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(0, 0, 0, 10)
        
        # Title bar with drag functionality
        title_bar = QLabel("📌 Stick To It")
        title_bar.setObjectName("titleLabel")
        title_bar.setAlignment(Qt.AlignCenter)
        title_bar.mousePressEvent = self.title_mouse_press
        title_bar.mouseMoveEvent = self.title_mouse_move
        main_layout.addWidget(title_bar)
        
        # Close button
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("position: absolute; top: 5px; right: 5px;")
        
        # Input area for new tasks
        input_container = QWidget()
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(10, 5, 10, 5)
        
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Add a new task...")
        self.task_input.returnPressed.connect(self.add_task_to_later)
        input_layout.addWidget(self.task_input)
        
        add_btn = QPushButton("+ Later")
        add_btn.clicked.connect(self.add_task_to_later)
        input_layout.addWidget(add_btn)
        
        add_now_btn = QPushButton("+ Now")
        add_now_btn.clicked.connect(self.add_task_to_now)
        input_layout.addWidget(add_now_btn)
        
        input_container.setLayout(input_layout)
        main_layout.addWidget(input_container)
        
        # Scroll area for tasks
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        scroll_content = QWidget()
        self.tasks_layout = QVBoxLayout()
        self.tasks_layout.setSpacing(5)
        self.tasks_layout.setContentsMargins(10, 5, 10, 5)
        scroll_content.setLayout(self.tasks_layout)
        scroll.setWidget(scroll_content)
        
        main_layout.addWidget(scroll, stretch=1)
        central_widget.setLayout(main_layout)
    
    def setup_reminder_timer(self):
        """Set up 2-hour reminder timer."""
        self.reminder_timer = QTimer()
        self.reminder_timer.timeout.connect(self.show_reminder)
        self.reminder_timer.start(2 * 60 * 60 * 1000)  # 2 hours in milliseconds
    
    def show_reminder(self):
        """Show reminder popup."""
        now_tasks = self.db.get_tasks_by_status("Now")
        incomplete_now = [t for t in now_tasks if not t['Completed Date']]
        
        if incomplete_now:
            msg = QMessageBox()
            msg.setWindowTitle("⏰ Reminder")
            msg.setText(f"You have {len(incomplete_now)} task(s) in progress!\n\nStay focused! 💪")
            msg.setIcon(QMessageBox.Information)
            msg.exec_()
        else:
            msg = QMessageBox()
            msg.setWindowTitle("⏰ Reminder")
            msg.setText("Time to check in!\n\nWhat are you working on? 🎯")
            msg.setIcon(QMessageBox.Information)
            msg.exec_()
    
    def add_task_to_later(self):
        """Add new task to Later category."""
        text = self.task_input.text().strip()
        if text:
            self.db.add_task(text, "Later")
            self.task_input.clear()
            self.refresh_tasks()
    
    def add_task_to_now(self):
        """Add new task to Now category."""
        text = self.task_input.text().strip()
        if text:
            self.db.add_task(text, "Now")
            self.task_input.clear()
            self.refresh_tasks()
    
    def refresh_tasks(self):
        """Reload and display all tasks."""
        # Clear existing tasks
        while self.tasks_layout.count():
            child = self.tasks_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Add "Now" section (always expanded)
        now_header = QLabel("🔥 Now")
        now_header.setObjectName("sectionHeader")
        self.tasks_layout.addWidget(now_header)
        
        now_tasks = self.db.get_tasks_by_status("Now")
        if now_tasks:
            for task in now_tasks:
                task_widget = TaskWidget(task, self)
                self.tasks_layout.addWidget(task_widget)
        else:
            empty_label = QLabel("No tasks in progress")
            empty_label.setObjectName("taskText")
            empty_label.setAlignment(Qt.AlignCenter)
            self.tasks_layout.addWidget(empty_label)
        
        # Add spacing
        self.tasks_layout.addSpacing(10)
        
        # Add "Later" section
        later_header = QLabel("📋 Later")
        later_header.setObjectName("sectionHeader")
        self.tasks_layout.addWidget(later_header)
        
        later_tasks = self.db.get_tasks_by_status("Later")
        if later_tasks:
            for task in later_tasks:
                task_widget = TaskWidget(task, self)
                self.tasks_layout.addWidget(task_widget)
        else:
            empty_label = QLabel("No tasks planned")
            empty_label.setObjectName("taskText")
            empty_label.setAlignment(Qt.AlignCenter)
            self.tasks_layout.addWidget(empty_label)
        
        # Add completed section
        completed_tasks = self.db.get_tasks_by_status("Completed")
        if completed_tasks:
            self.tasks_layout.addSpacing(10)
            completed_header = QLabel("✅ Completed")
            completed_header.setObjectName("sectionHeader")
            self.tasks_layout.addWidget(completed_header)
            
            for task in completed_tasks[-5:]:  # Show last 5 completed
                task_widget = TaskWidget(task, self)
                self.tasks_layout.addWidget(task_widget)
        
        self.tasks_layout.addStretch()
    
    def title_mouse_press(self, event):
        """Handle mouse press on title bar for dragging."""
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()
    
    def title_mouse_move(self, event):
        """Handle mouse move on title bar for dragging."""
        if self.dragging:
            self.move(self.mapToGlobal(event.pos() - self.offset))


def main():
    app = QApplication(sys.argv)
    
    # Set application font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = StickyNoteApp()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()