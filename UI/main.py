# main.py
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QStackedLayout
from PyQt5.QtCore import Qt
from .login import LoginPage
from .home import HomePage
from .chat import ChatPage

class ChatApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SecureChat")
        self.resize(1100, 700)
        self.setMinimumSize(900, 600)

        self.token = None
        self.user_id = None
        self.private_key = None
        self.current_chat_id = None

        self.layout = QStackedLayout()
        self.setLayout(self.layout)

        self.login_page = LoginPage(self)
        self.home_page = HomePage(self)
        self.chat_page = ChatPage(self)

        self.layout.addWidget(self.login_page)
        self.layout.addWidget(self.home_page)
        self.layout.addWidget(self.chat_page)

        self.layout.setCurrentWidget(self.login_page)

        # Global Style
        self.setStyleSheet("""
            * { font-family: 'Segoe UI', 'Inter', sans-serif; }
            QWidget { background-color: #111; color: #eee; }
            QLineEdit, QTextEdit { 
                background-color: #222; 
                border: 1px solid #333; 
                border-radius: 12px; 
                padding: 10px; 
                color: white;
            }
            QPushButton {
                background-color: #0088cc;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 10px 16px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #0099ee; }
            QListWidget::item { padding: 12px; border-bottom: 1px solid #333; }
            QListWidget::item:hover { background-color: #2a2a2a; }
            QListWidget::item:selected { background-color: #0088cc; }
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = ChatApp()
    window.show()
    sys.exit(app.exec_())