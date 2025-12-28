import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QLineEdit, 
                             QScrollArea, QCheckBox, QMessageBox, QSystemTrayIcon,
                             QMenu, QAction)
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPainter, QColor
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
        layout.setContentsMargins(0, 0, 0, 0)
        
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
            self.start_btn = QPushButton("▶️")
            self.start_btn.setObjectName("smallBtn")
            self.start_btn.setToolTip("Start working on this")
            self.start_btn.clicked.connect(self.mark_in_progress)
            self.start_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(0,0,0,0);
                    border: none;
                    font-size: 14px;
                    font-weight: bold;
                    border-radius: 0px;
                }
                QPushButton:hover {
                    background-color: #FFC107;
                }
            """)
            layout.addWidget(self.start_btn)
        
        # Delete button
        self.delete_btn = QPushButton("✕")
        self.delete_btn.setObjectName("smallBtn")
        self.delete_btn.setToolTip("Delete task")
        self.delete_btn.clicked.connect(self.delete_task)
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(0,0,0,0);
                border: none;
                font-size: 14px;
                font-weight: bold;
                border-radius: 0px;
            }
            QPushButton:hover {
                background-color: #FFC107;
            }
        """)
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
        self.setup_system_tray()
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
    
    def create_tray_icon(self):
        """Create a simple tray icon."""
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw a yellow sticky note
        painter.setBrush(QColor(255, 235, 59))
        painter.setPen(QColor(249, 168, 37))
        painter.drawRoundedRect(4, 4, 56, 56, 8, 8)
        
        # Draw a pin
        painter.setBrush(QColor(244, 67, 54))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(26, 8, 12, 12)
        
        painter.end()
        return QIcon(pixmap)
    
    def setup_system_tray(self):
        """Set up system tray icon and menu."""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.create_tray_icon())
        self.tray_icon.setToolTip("📌 Stick To It - Running")
        
        # Create tray menu
        tray_menu = QMenu()
        
        show_action = QAction("Show Window", self)
        show_action.triggered.connect(self.show_window)
        tray_menu.addAction(show_action)
        
        hide_action = QAction("Hide Window", self)
        hide_action.triggered.connect(self.hide)
        tray_menu.addAction(hide_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        
        # Double-click to show/hide
        self.tray_icon.activated.connect(self.tray_icon_activated)
        
        # Show the tray icon
        self.tray_icon.show()
        
        # Show initial message
        self.tray_icon.showMessage(
            "📌 Stick To It",
            "App is running in the background. Click the tray icon to show/hide.",
            QSystemTrayIcon.Information,
            2000
        )
    
    def tray_icon_activated(self, reason):
        """Handle tray icon clicks."""
        if reason == QSystemTrayIcon.DoubleClick:
            if self.isVisible():
                self.hide()
            else:
                self.show_window()
    
    def show_window(self):
        """Show and raise the window."""
        self.showNormal()
        self.raise_()
        self.activateWindow()
    
    def quit_application(self):
        """Properly quit the application."""
        self.tray_icon.hide()
        QApplication.quit()
    
    def closeEvent(self, event):
        """Override close event to hide instead of quit."""
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "📌 Still Running",
            "Stick To It is running in the background. Right-click the tray icon to quit.",
            QSystemTrayIcon.Information,
            2000
        )
    
    def setup_ui(self):
        """Create the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title bar container with drag functionality and buttons
        title_container = QWidget()
        title_container_layout = QHBoxLayout()
        title_container_layout.setContentsMargins(0, 0, 0, 0)
        title_container_layout.setSpacing(0)
        
        # Title bar with drag functionality
        self.title_bar = QLabel("📌 Stick To It")
        self.title_bar.setObjectName("titleLabel")
        self.title_bar.setAlignment(Qt.AlignCenter)
        self.title_bar.mousePressEvent = self.title_mouse_press
        self.title_bar.mouseMoveEvent = self.title_mouse_move
        title_container_layout.addWidget(self.title_bar, stretch=1)
        
        # Minimize button
        minimize_btn = QPushButton("—")
        minimize_btn.setFixedSize(36, 36)
        minimize_btn.setObjectName("smallBtn")
        minimize_btn.setToolTip("Minimize to Tray")
        minimize_btn.clicked.connect(self.hide)
        minimize_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFF9C4;
                border: none;
                font-size: 14px;
                font-weight: bold;
                border-radius: 0px;
            }
            QPushButton:hover {
                background-color: #FFC107;
            }
        """)
        title_container_layout.addWidget(minimize_btn)
        
        # Close button (now hides to tray)
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(36, 36)
        close_btn.setObjectName("smallBtn")
        close_btn.setToolTip("Hide to Tray")
        close_btn.clicked.connect(self.hide)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFF9C4;
                border: none;
                font-size: 14px;
                font-weight: bold;
                border-radius: 0px;
            }
            QPushButton:hover {
                background-color: #E65100;
            }
        """)
        title_container_layout.addWidget(close_btn)
        
        title_container.setLayout(title_container_layout)
        main_layout.addWidget(title_container)
        
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
        central_widget.setLayout(main_layout)# Input area for new tasks
        input_container = QWidget()
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(10, 5, 10, 5)
        
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Add a new task...")
        self.task_input.returnPressed.connect(self.add_task_to_later)
        input_layout.addWidget(self.task_input)
        
        add_now_btn = QPushButton("🔥")
        add_now_btn.setFixedSize(32, 32)
        add_now_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(0,0,0,0);
                border: none;
                font-size: 20px;
                font-weight: bold;
                border-radius: 0px;
            }
            QPushButton:hover {
                background-color: #FFC107;
            }
        """)
        add_now_btn.clicked.connect(self.add_task_to_now)
        input_layout.addWidget(add_now_btn)
        
        add_btn = QPushButton("📅")
        add_btn.setFixedSize(32, 32)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(0,0,0,0);
                border: none;
                font-size: 20px;
                font-weight: bold;
                border-radius: 0px;
            }
            QPushButton:hover {
                background-color: #FFC107;
            }
        """)
        add_btn.clicked.connect(self.add_task_to_later)
        input_layout.addWidget(add_btn)
        
        input_container.setLayout(input_layout)
        main_layout.addWidget(input_container)
    
    def setup_reminder_timer(self):
        """Set up 2-hour reminder timer."""
        self.reminder_timer = QTimer()
        self.reminder_timer.timeout.connect(self.show_reminder)
        self.reminder_timer.start(2 * 60 * 60 * 1000)  # 2 hours in milliseconds
    
    def show_reminder(self):
        """Show reminder popup and maximize window."""
        # Show the window first
        self.show_window()
        
        # Then show the reminder
        now_tasks = self.db.get_tasks_by_status("Now")
        incomplete_now = [t for t in now_tasks if not t['Completed Date']]
        
        if incomplete_now:
            msg = QMessageBox(self)
            msg.setWindowTitle("⏰ Reminder")
            msg.setText(f"You have {len(incomplete_now)} task(s) in progress!\n\nStay focused! 💪")
            msg.setIcon(QMessageBox.Information)
            msg.setWindowFlags(Qt.WindowStaysOnTopHint)
            msg.exec_()
        else:
            msg = QMessageBox(self)
            msg.setWindowTitle("⏰ Reminder")
            msg.setText("Time to check in!\n\nWhat are you working on? 🎯")
            msg.setIcon(QMessageBox.Information)
            msg.setWindowFlags(Qt.WindowStaysOnTopHint)
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
        later_header = QLabel("📅 Later")
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
    
    # Set application to not quit when last window closes (for system tray)
    app.setQuitOnLastWindowClosed(False)
    
    # Set application font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = StickyNoteApp()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()