# login.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QFrame, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QColor, QFont, QIcon
import threading
from services import api_client, crypto_client # <--- CHỈ CẦN API_CLIENT

class LoginPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.password_visible = False
        self.init_ui()

    def init_ui(self):
        # Style chung cho trang
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f2f5; /* Nền xám nhạt của Telegram */
            }
            QFrame#container {
                background-color: #ffffff;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
            QLabel {
                color: #222;
                font-family: 'Segoe UI', 'Inter', sans-serif;
            }
            QLineEdit {
                background-color: #f0f2f5;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 12px 14px;
                color: #111;
                font-size: 14px;
                font-family: 'Segoe UI', 'Inter', sans-serif;
            }
            QLineEdit:focus {
                border: 2px solid #0088cc;
                padding: 11px 13px; /* Giữ nguyên kích thước */
                background-color: #ffffff;
            }
            QPushButton#primary {
                background-color: #0088cc;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 16px;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton#primary:hover {
                background-color: #0099ee;
            }
            QPushButton#secondary {
                background-color: #e7ebee;
                color: #111;
                border: none;
                border-radius: 8px;
                padding: 12px 16px;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton#secondary:hover {
                background-color: #dfe3e7;
            }
            QPushButton#toggleBtn {
                background-color: transparent;
                color: #777;
                border: none;
                font-weight: bold;
                font-size: 13px;
                padding: 0 8px;
            }
            QPushButton#toggleBtn:hover {
                color: #0088cc;
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

        # Icon
        icon_label = QLabel("💬") # Biểu tượng chat đơn giản
        icon_label.setFont(QFont("Segoe UI", 60))
        icon_label.setAlignment(Qt.AlignCenter)
        header.addWidget(icon_label)

        title = QLabel("SecureChat")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont("Segoe UI", 28, QFont.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: #0088cc;")
        header.addWidget(title)

        subtitle = QLabel("Đăng nhập để tiếp tục")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle_font = QFont("Segoe UI", 14)
        subtitle.setFont(subtitle_font)
        subtitle.setStyleSheet("color: #777; margin-bottom: 25px;")
        header.addWidget(subtitle)

        content.addLayout(header)

        # Form container
        container = QFrame()
        container.setObjectName("container") # Áp dụng style QFrame#container
        container.setMinimumWidth(380)
        container.setMaximumWidth(380)
        
        # Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        container.setGraphicsEffect(shadow)

        form = QVBoxLayout(container)
        form.setSpacing(14)
        form.setContentsMargins(30, 30, 30, 30)

        # Username
        username_label = QLabel("Username")
        username_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #333;")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nhập username")
        self.username_input.setMinimumHeight(44)
        form.addWidget(username_label)
        form.addWidget(self.username_input)

        # Password
        password_label = QLabel("Password")
        password_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #333;")
        form.addWidget(password_label)

        password_container = QHBoxLayout()
        password_container.setSpacing(0)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Nhập mật khẩu")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(44)
        
        self.toggle_btn = QPushButton("Show")
        self.toggle_btn.setObjectName("toggleBtn")
        self.toggle_btn.setFixedWidth(50)
        self.toggle_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_btn.clicked.connect(self.toggle_password_visibility)
        
        # Thêm input và nút vào layout
        pass_widget = QWidget()
        pass_layout_inner = QHBoxLayout(pass_widget)
        pass_layout_inner.setContentsMargins(0,0,0,0)
        pass_layout_inner.setSpacing(0)
        pass_layout_inner.addWidget(self.password_input)
        pass_layout_inner.addWidget(self.toggle_btn)
        # Đảm bảo nút "Show" nằm bên trong QLineEdit (về mặt thị giác)
        self.password_input.setStyleSheet("padding-right: 55px;") 
        pass_widget.setLayout(pass_layout_inner)
        
        form.addWidget(pass_widget)

        # Button row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        
        self.login_btn = QPushButton("Đăng nhập")
        self.login_btn.setObjectName("primary")
        self.register_btn = QPushButton("Đăng ký")
        self.register_btn.setObjectName("secondary")
        
        self.login_btn.setMinimumHeight(44)
        self.register_btn.setMinimumHeight(44)
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.register_btn.setCursor(Qt.PointingHandCursor)
        
        btn_row.addWidget(self.register_btn)
        btn_row.addWidget(self.login_btn)
        form.addSpacing(15)
        form.addLayout(btn_row)

        content.addWidget(container)

        # Message label
        self.message_label = QLabel("")
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setStyleSheet("color: #D32F2F; font-size: 14px; margin-top: 16px; font-weight: 500;")
        content.addWidget(self.message_label)

        main_layout.addLayout(content)

        # Connect actions
        self.login_btn.clicked.connect(self.do_login)
        self.register_btn.clicked.connect(self.go_to_register) # <--- SỬA Ở ĐÂY

        # Cho phép nhấn Enter để đăng nhập
        self.username_input.returnPressed.connect(self.do_login)
        self.password_input.returnPressed.connect(self.do_login)

    # <--- HÀM MỚI
    def go_to_register(self):
        self.parent.layout.setCurrentWidget(self.parent.register_page)

    def toggle_password_visibility(self):
        self.password_visible = not self.password_visible
        if self.password_visible:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.toggle_btn.setText("Hide")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.toggle_btn.setText("Show")

    def show_message(self, message, error=True):
        color = "#D32F2F" if error else "#0088cc" # Đỏ cho lỗi, xanh cho thành công
        self.message_label.setStyleSheet(f"color: {color}; font-size: 14px; font-weight: 500; margin-top: 16px;")
        self.message_label.setText(message)

    # <--- XÓA HÀM DO_REGISTER()
    
    def do_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        if not username or not password:
            self.show_message("Vui lòng điền đầy đủ thông tin.", error=True)
            return

        self.login_btn.setEnabled(False)
        self.register_btn.setEnabled(False)
        self.show_message("Đang đăng nhập...", error=False)

        # Chạy trong thread để không block UI
        def login_thread():
            token, user_id, status, data = api_client.login(username, password)
            if status == 200:
                try:
                    private_key = crypto_client.load_private_key(username, password)
                except Exception as e:
                    self.show_message(f"Lỗi khóa: {str(e)}", error=True)
                    self.login_btn.setEnabled(True)
                    self.register_btn.setEnabled(True)
                    return

                # Lưu thông tin vào parent (ChatApp)
                self.parent.token = token
                self.parent.user_id = user_id
                self.parent.private_key = private_key
                
                # Xóa thông tin trên form
                self.username_input.clear()
                self.password_input.clear()
                self.show_message("", error=False) # Xóa thông báo lỗi/thành công

                # Kết nối socket và tải chat
                self.parent.home_page.connect_socket()
                self.parent.home_page.refresh_chats()
                self.parent.home_page.set_current_user_label() # Cập nhật tên user
                
                # Chuyển trang
                self.parent.layout.setCurrentWidget(self.parent.home_page)
            else:
                error_msg = data.get("msg", "Đăng nhập thất bại")
                self.show_message(f"{error_msg}", error=True)
            
            self.login_btn.setEnabled(True)
            self.register_btn.setEnabled(True)

        threading.Thread(target=login_thread, daemon=True).start()