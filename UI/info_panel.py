# info_panel.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from services import api_client

class InfoPanel(QWidget):
    def __init__(self, parent_app):
        super().__init__()
        self.parent_app = parent_app # Đây là ChatApp (root)
        self.current_user_id = None
        self.init_ui()

    def init_ui(self):
        self.setFixedWidth(300)
        self.setStyleSheet("""
            QWidget {
                background-color: #f7f9fa;
                border-left: 1px solid #e0e0e0;
                font-family: 'Segoe UI', 'Inter', sans-serif;
            }
            QLabel {
                border: none;
                background-color: transparent;
            }
            QFrame#header {
                border-bottom: 1px solid #e0e0e0;
                background-color: #ffffff;
            }
            QLabel#header_title {
                font-size: 16px;
                font-weight: 600;
                color: #111;
            }
            QPushButton#close_btn {
                font-size: 18px;
                font-weight: 700;
                color: #777;
                border: none;
                background: transparent;
                padding: 5px;
            }
            QPushButton#close_btn:hover {
                color: #111;
            }
            QLabel#avatar {
                font-size: 60px;
                qproperty-alignment: 'AlignCenter';
                padding: 20px;
            }
            QLabel#full_name {
                font-size: 18px;
                font-weight: 600;
                color: #111;
                qproperty-alignment: 'AlignCenter';
            }
            QLabel#username {
                font-size: 14px;
                color: #777;
                qproperty-alignment: 'AlignCenter';
                margin-bottom: 15px;
            }
            QFrame#separator {
                background-color: #e0e0e0;
                min-height: 1px;
                max-height: 1px;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        header_frame = QFrame()
        header_frame.setObjectName("header")
        header_frame.setFixedHeight(60)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(15, 0, 10, 0)
        
        self.header_title = QLabel("Thông tin")
        self.header_title.setObjectName("header_title")
        
        self.close_btn = QPushButton("❌")
        self.close_btn.setObjectName("close_btn")
        self.close_btn.setFixedSize(32, 32)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        # Nút close sẽ được kết nối từ home_page
        
        header_layout.addWidget(self.header_title)
        header_layout.addStretch()
        header_layout.addWidget(self.close_btn)
        main_layout.addWidget(header_frame)

        # Content Area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(10)
        content_layout.setAlignment(Qt.AlignTop)

        # Profile Info
        self.avatar_label = QLabel("👤")
        self.avatar_label.setObjectName("avatar")
        
        self.full_name_label = QLabel("...")
        self.full_name_label.setObjectName("full_name")
        
        self.username_label = QLabel("@...")
        self.username_label.setObjectName("username")
        
        content_layout.addWidget(self.avatar_label)
        content_layout.addWidget(self.full_name_label)
        content_layout.addWidget(self.username_label)
        
        # Separator
        separator = QFrame()
        separator.setObjectName("separator")
        content_layout.addWidget(separator)
        
        # Các thông tin khác (đang chờ)
        self.bio_label = QLabel("...")
        self.bio_label.setWordWrap(True)
        self.bio_label.setStyleSheet("font-size: 13px; color: #333; margin-top: 15px;")
        content_layout.addWidget(self.bio_label)
        
        # Shared Media (Placeholder)
        media_label = QLabel("Shared Media")
        media_label.setStyleSheet("font-size: 15px; font-weight: 600; margin-top: 20px;")
        content_layout.addWidget(media_label)
        
        media_placeholder = QLabel("Không có media chia sẻ.")
        media_placeholder.setStyleSheet("font-size: 13px; color: #777;")
        content_layout.addWidget(media_placeholder)

        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

    def load_user_info(self, user_id):
        if not user_id or user_id == self.current_user_id:
            return # Không tải lại nếu vẫn là user đó

        self.current_user_id = user_id
        token = self.parent_app.token
        
        status, data = api_client.get_user_info(token, user_id)
        if status == 200:
            self.full_name_label.setText(data.get("full_name") or "Không có tên")
            self.username_label.setText(f"@{data.get('username')}")
            self.bio_label.setText(data.get('bio') or "Không có tiểu sử.")
            self.header_title.setText(f"Thông tin User {user_id}")
        else:
            self.full_name_label.setText("Không thể tải")
            self.username_label.setText("@error")
            self.bio_label.setText("")