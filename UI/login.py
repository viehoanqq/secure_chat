from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QFrame, QGraphicsDropShadowEffect, QCheckBox
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QColor, QFont, QIcon
import threading
from services import api_client, crypto_client

class ModernLineEdit(QLineEdit):
    """Custom QLineEdit with modern styling and animations"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_focused = False
        self.setup_styles()
    
    def setup_styles(self):
        self.setStyleSheet("""
            QLineEdit {
                background-color: #1e293b;
                border: 2px solid #334155;
                border-radius: 12px;
                padding: 12px 16px;
                color: #f8fafc;
                font-size: 14px;
                font-family: 'Segoe UI', 'Inter', sans-serif;
            }
            QLineEdit:focus {
                border: 2px solid #0ea5e9;
                background-color: #1e293b;
            }
        """)
    
    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.is_focused = True
        
    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.is_focused = False

class LoginPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.password_visible = False
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QWidget {
                background: linear-gradient(135deg, #0f172a 0%, #1a202c 100%);
            }
            QLabel {
                color: #e2e8f0;
                font-family: 'Segoe UI', 'Inter', sans-serif;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                            stop:0 #06b6d4, stop:1 #3b82f6);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 12px 16px;
                font-weight: bold;
                font-size: 15px;
                font-family: 'Segoe UI', 'Inter', sans-serif;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                            stop:0 #0891b2, stop:1 #2563eb);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                            stop:0 #06a8a8, stop:1 #1d4ed8);
            }
            QCheckBox {
                color: #cbd5e1;
                spacing: 8px;
                font-size: 13px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
            }
            QCheckBox::indicator:unchecked {
                background-color: #1e293b;
                border: 2px solid #334155;
            }
            QCheckBox::indicator:checked {
                background-color: #0ea5e9;
                border: 2px solid #0ea5e9;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setAlignment(Qt.AlignCenter)

        # Content container
        content = QVBoxLayout()
        content.setSpacing(0)
        content.setAlignment(Qt.AlignCenter)

        # Header section
        header = QVBoxLayout()
        header.setSpacing(8)
        header.setAlignment(Qt.AlignCenter)

        # <CHANGE> improved title styling with modern font
        title = QLabel("💬 SecureChat")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont("Segoe UI", 36)
        title_font.setWeight(QFont.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: #06b6d4; letter-spacing: 1px;")
        header.addWidget(title)

        # <CHANGE> enhanced subtitle
        subtitle = QLabel("End-to-End Encrypted Messaging")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle_font = QFont("Segoe UI", 13)
        subtitle.setFont(subtitle_font)
        subtitle.setStyleSheet("color: #94a3b8; margin-bottom: 30px; font-weight: 300;")
        header.addWidget(subtitle)

        content.addLayout(header)

        # Form container with shadow
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #1e293b;
                border-radius: 20px;
                border: 1px solid #334155;
                padding: 40px;
            }
        """)
        
        # <CHANGE> added drop shadow for depth
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 200))
        shadow.setOffset(0, 10)
        container.setGraphicsEffect(shadow)

        form = QVBoxLayout(container)
        form.setSpacing(16)

        # Username input
        username_label = QLabel("Username")
        username_label.setStyleSheet("color: #cbd5e1; font-size: 15px; font-weight: 800; margin-top: 8px; border: none;")
        self.username_input = ModernLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setMinimumHeight(44)
        form.addWidget(username_label)
        form.addWidget(self.username_input)

        # Password input with toggle
        password_label = QLabel("Password")
        password_label.setStyleSheet("color: #cbd5e1; font-size: 15px; font-weight: 800; margin-top: 8px;  border: none")
        form.addWidget(password_label)

        password_container = QHBoxLayout()
        password_container.setSpacing(8)
        self.password_input = ModernLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(44)
        
        # <CHANGE> added toggle password visibility button
        toggle_btn = QPushButton("Show")
        toggle_btn.setFixedWidth(60)
        toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #334155;
                color: #cbd5e1;
                border: 1px solid #475569;
                border-radius: 8px;
                padding: 8px;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #475569;
            }
        """)
        toggle_btn.clicked.connect(self.toggle_password_visibility)
        self.toggle_btn = toggle_btn
        
        password_container.addWidget(self.password_input)
        password_container.addWidget(toggle_btn)
        form.addLayout(password_container)

        # <CHANGE> added remember me checkbox and forgot password link
        extra_row = QHBoxLayout()
        extra_row.setSpacing(0)
        
        remember_check = QCheckBox("Remember me")
        remember_check.setStyleSheet("QCheckBox { color: #94a3b8; font-size: 12px; }")
        extra_row.addWidget(remember_check)
        

        extra_row.addStretch()
        
        form.addLayout(extra_row)

        # Button row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        
        self.login_btn = QPushButton("Sign In")
        self.register_btn = QPushButton("Sign Up")
        
        self.login_btn.setMinimumHeight(44)
        self.register_btn.setMinimumHeight(44)
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.register_btn.setCursor(Qt.PointingHandCursor)
        
        btn_row.addWidget(self.login_btn)
        btn_row.addWidget(self.register_btn)
        form.addSpacing(8)
        form.addLayout(btn_row)

        content.addWidget(container)

        # Message label
        self.message_label = QLabel("")
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setStyleSheet("color: #ef4444; font-size: 13px; margin-top: 16px; font-weight: 500;")
        content.addWidget(self.message_label)

        main_layout.addLayout(content)

        # Connect actions
        self.login_btn.clicked.connect(self.do_login)
        self.register_btn.clicked.connect(self.do_register)

    # <CHANGE> added password visibility toggle method
    def toggle_password_visibility(self):
        self.password_visible = not self.password_visible
        if self.password_visible:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.toggle_btn.setText("Hide")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.toggle_btn.setText("Show")

    def do_register(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        if not username or not password:
            self.show_message("Please fill in all fields.", error=True)
            return
        try:
            crypto_client.register_and_save_key(username, password)
            self.show_message("Registration successful! You can login now.", error=False)
            self.username_input.clear()
            self.password_input.clear()
        except Exception as e:
            self.show_message(f"Registration failed: {str(e)}", error=True)

    def do_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        if not username or not password:
            self.show_message("Please fill in all fields.", error=True)
            return

        token, user_id, status, data = api_client.login(username, password)
        if status == 200:
            try:
                private_key = crypto_client.load_private_key(username, password)
            except Exception as e:
                self.show_message(f"Key error: {str(e)}", error=True)
                return

            self.parent.token = token
            self.parent.user_id = user_id
            self.parent.private_key = private_key
            self.show_message("Login successful!", error=False)

            self.parent.home_page.connect_socket()
            self.parent.home_page.refresh_chats()
            self.parent.layout.setCurrentWidget(self.parent.home_page)
        else:
            error_msg = data.get("msg", "Login failed")
            self.show_message(f"{error_msg}", error=True)

    # <CHANGE> added helper method for showing messages with styling
    def show_message(self, message, error=True):
        color = "#ef4444" if error else "#22c55e"
        self.message_label.setStyleSheet(f"color: {color}; font-size: 13px; font-weight: 500;")
        self.message_label.setText(message)