# register_page.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QFrame, QGraphicsDropShadowEffect, QComboBox, QDateEdit, QMessageBox
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QFont
import threading
from services import crypto_client # Chúng ta chỉ cần crypto_client ở đây

class RegisterPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f2f5;
                color: #222;
                font-family: 'Segoe UI', 'Inter', sans-serif;
            }
            QFrame#container {
                background-color: #ffffff;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
            QLabel { color: #222; }
            QLabel#title {
                color: #0088cc;
                font-size: 28px;
                font-weight: 700;
                margin-bottom: 20px;
            }
            QLineEdit, QComboBox, QDateEdit {
                background-color: #f0f2f5;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 11px 14px;
                color: #111;
                font-size: 14px;
                min-height: 22px; /* 11+11+22 = 44px total */
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
                border: 2px solid #0088cc;
                padding: 10px 13px;
                background-color: #ffffff;
            }
            QComboBox::drop-down { border: none; }
            QComboBox::down-arrow { image: none; } /* Tùy chỉnh nếu muốn */
            
            QPushButton#primary {
                background-color: #0088cc;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 16px;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton#primary:hover { background-color: #0099ee; }
            
            QPushButton#secondary {
                background-color: transparent;
                color: #0088cc;
                border: none;
                font-weight: 600;
                font-size: 14px;
                padding: 8px;
            }
            QPushButton#secondary:hover { color: #0099ee; }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)

        # Form container
        container = QFrame()
        container.setObjectName("container")
        container.setMinimumWidth(400)
        container.setMaximumWidth(400)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        container.setGraphicsEffect(shadow)

        form_layout = QVBoxLayout(container)
        form_layout.setSpacing(14)
        form_layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("Tạo tài khoản")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(title)

        # Form fields
        self.username_input = QLineEdit(placeholderText="Tên đăng nhập")
        self.password_input = QLineEdit(placeholderText="Mật khẩu", echoMode=QLineEdit.Password)
        self.confirm_password_input = QLineEdit(placeholderText="Xác nhận mật khẩu", echoMode=QLineEdit.Password)
        self.full_name_input = QLineEdit(placeholderText="Họ và tên")
        
        self.gender_input = QComboBox()
        self.gender_input.addItems(["Other", "Male", "Female"])
        
        self.dob_input = QDateEdit(calendarPopup=True)
        self.dob_input.setDisplayFormat("yyyy-MM-dd")
        self.dob_input.setDate(QDate.currentDate().addYears(-18)) # Gợi ý
        self.dob_input.setMaximumDate(QDate.currentDate())

        form_layout.addWidget(self.username_input)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(self.confirm_password_input)
        form_layout.addWidget(self.full_name_input)
        form_layout.addWidget(self.gender_input)
        form_layout.addWidget(QLabel("Ngày sinh:"))
        form_layout.addWidget(self.dob_input)

        form_layout.addSpacing(15)
        
        self.register_btn = QPushButton("Đăng Ký")
        self.register_btn.setObjectName("primary")
        self.register_btn.setMinimumHeight(44)
        self.register_btn.setCursor(Qt.PointingHandCursor)
        form_layout.addWidget(self.register_btn)

        self.back_btn = QPushButton("Quay lại Đăng nhập")
        self.back_btn.setObjectName("secondary")
        self.back_btn.setCursor(Qt.PointingHandCursor)
        form_layout.addWidget(self.back_btn)

        self.message_label = QLabel("")
        self.message_label.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(self.message_label)

        main_layout.addWidget(container)

        # Connect actions
        self.register_btn.clicked.connect(self.do_register)
        self.back_btn.clicked.connect(self.go_to_login)

    def go_to_login(self):
        self.parent.layout.setCurrentWidget(self.parent.login_page)

    def show_message(self, message, error=True):
        color = "#D32F2F" if error else "#0088cc"
        self.message_label.setStyleSheet(f"color: {color}; font-size: 14px; font-weight: 500; margin-top: 10px;")
        self.message_label.setText(message)

    def do_register(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        confirm_password = self.confirm_password_input.text().strip()
        full_name = self.full_name_input.text().strip()
        gender = self.gender_input.currentText().lower()
        dob = self.dob_input.date().toString("yyyy-MM-dd")

        if not all([username, password, confirm_password, full_name]):
            self.show_message("Vui lòng điền tất cả các trường.", error=True)
            return
        
        if password != confirm_password:
            self.show_message("Mật khẩu xác nhận không khớp.", error=True)
            return

        self.register_btn.setEnabled(False)
        self.show_message("Đang xử lý...", error=False)

        # Chạy trong thread để không block UI
        def register_thread():
            try:
                # Gọi crypto_client với các trường mới
                crypto_client.register_and_save_key(
                    username, 
                    password, 
                    full_name=full_name, 
                    gender=gender, 
                    date_of_birth=dob
                )
                self.show_message("Đăng ký thành công! Quay lại để đăng nhập.", error=False)
                # Xóa form
                self.username_input.clear()
                self.password_input.clear()
                self.confirm_password_input.clear()
                self.full_name_input.clear()
            except Exception as e:
                self.show_message(f"Đăng ký thất bại: {str(e)}", error=True)
            finally:
                self.register_btn.setEnabled(True)
        
        threading.Thread(target=register_thread, daemon=True).start()