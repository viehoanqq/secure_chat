from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QFrame
from PyQt5.QtCore import Qt
import threading
from services import api_client, crypto_client

class LoginPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QLabel, QLineEdit, QPushButton {
                font-family: 'Segoe UI', 'Inter', sans-serif;
            }
            QLineEdit {
                background-color: #1f1f1f;
                border: 1px solid #333;
                border-radius: 8px;
                padding: 10px;
                color: white;
            }
            QLineEdit:focus {
                border: 1px solid #0088cc;
            }
            QPushButton {
                background-color: #0088cc;
                color: white;
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0099ee;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(15)

        title = QLabel("SecureChat")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #0088cc; margin-bottom: 10px;")
        layout.addWidget(title)

        subtitle = QLabel("End-to-end encrypted chat")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #aaa; font-size: 14px; margin-bottom: 25px;")
        layout.addWidget(subtitle)

        # Input container
        container = QFrame()
        form = QVBoxLayout(container)
        form.setSpacing(10)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)

        form.addWidget(self.username_input)
        form.addWidget(self.password_input)

        btn_row = QHBoxLayout()
        self.login_btn = QPushButton("Login")
        self.register_btn = QPushButton("Register")
        btn_row.addWidget(self.login_btn)
        btn_row.addWidget(self.register_btn)
        form.addLayout(btn_row)

        layout.addWidget(container)

        self.message_label = QLabel("")
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setStyleSheet("color: #ff6b6b; margin-top: 10px;")
        layout.addWidget(self.message_label)

        self.login_btn.clicked.connect(self.do_login)
        self.register_btn.clicked.connect(self.do_register)

    def do_register(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        if not username or not password:
            self.message_label.setText("Please fill in all fields")
            return
        try:
            crypto_client.register_and_save_key(username, password)
            self.message_label.setStyleSheet("color:#51cf66;")
            self.message_label.setText("✅ Register successful! You can login now.")
        except Exception as e:
            self.message_label.setStyleSheet("color:#ff6b6b;")
            self.message_label.setText(f"Register failed: {e}")

    def do_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        if not username or not password:
            self.message_label.setText("Please fill in all fields")
            return

        token, user_id, status, data = api_client.login(username, password)
        if status == 200:
            try:
                private_key = crypto_client.load_private_key(username, password)
            except Exception as e:
                self.message_label.setText(f"Key error: {e}")
                return

            self.parent.token = token
            self.parent.user_id = user_id
            self.parent.private_key = private_key
            self.message_label.setText('<span style="color:#51cf66">Login success!</span>')

            threading.Thread(target=self.parent.home_page.connect_socket, daemon=True).start()
            self.parent.home_page.refresh_chats()
            self.parent.layout.setCurrentWidget(self.parent.home_page)
        else:
            self.message_label.setText(f'<span style="color:#ff6b6b">{data.get("msg", "Login failed")}</span>')
