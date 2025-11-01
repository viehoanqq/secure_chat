# profile_page.py
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, 
    QDateEdit, QTextEdit, QPushButton, QLabel, QMessageBox, QDialogButtonBox
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from services import api_client

class ProfilePage(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        # parent ở đây là ChatApp (self.parent.parent từ HomePage)
        self.parent_app = parent 
        
        self.setWindowTitle("Thông tin cá nhân")
        self.setMinimumSize(450, 400)
        self.init_ui()
        self.load_profile_data()

    def init_ui(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                font-family: 'Segoe UI', 'Inter', sans-serif;
            }
            QLabel {
                font-size: 14px;
                color: #333;
                padding-top: 5px;
            }
            QLineEdit, QComboBox, QDateEdit, QTextEdit {
                background-color: #f0f2f5;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 10px 12px;
                color: #111;
                font-size: 14px;
                min-height: 24px;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus {
                border: 2px solid #0088cc;
                padding: 9px 11px;
                background-color: #ffffff;
            }
            QLineEdit#username {
                background-color: #e7ebee;
                color: #555;
            }
            QPushButton {
                background-color: #0088cc;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 11px 16px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #0099ee; }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignRight)

        # Fields
        self.username_label = QLineEdit()
        self.username_label.setObjectName("username")
        self.username_label.setReadOnly(True)
        
        self.full_name_input = QLineEdit()
        self.bio_input = QTextEdit()
        self.bio_input.setPlaceholderText("Giới thiệu về bạn...")
        self.bio_input.setFixedHeight(80)

        self.gender_input = QComboBox()
        self.gender_input.addItems(["other", "male", "female"])
        
        self.dob_input = QDateEdit(calendarPopup=True)
        self.dob_input.setDisplayFormat("yyyy-MM-dd")
        self.dob_input.setMaximumDate(QDate.currentDate())

        form_layout.addRow(QLabel("Tên đăng nhập:"), self.username_label)
        form_layout.addRow(QLabel("Họ và tên:"), self.full_name_input)
        form_layout.addRow(QLabel("Giới tính:"), self.gender_input)
        form_layout.addRow(QLabel("Ngày sinh:"), self.dob_input)
        form_layout.addRow(QLabel("Tiểu sử:"), self.bio_input)
        
        layout.addLayout(form_layout)

        # Buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.save_profile)
        self.button_box.rejected.connect(self.reject)
        
        # Style các nút
        self.button_box.button(QDialogButtonBox.Save).setStyleSheet("background-color: #0088cc;")
        self.button_box.button(QDialogButtonBox.Cancel).setStyleSheet(
            "background-color: #e7ebee; color: #333;"
        )

        layout.addWidget(self.button_box)

    def load_profile_data(self):
        token = self.parent_app.token
        user_id = self.parent_app.user_id

        if not token or not user_id:
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy thông tin xác thực.")
            self.reject()
            return

        status, data = api_client.get_user_info(token, user_id)
        if status == 200:
            self.username_label.setText(data.get("username", ""))
            self.full_name_input.setText(data.get("full_name", ""))
            self.bio_input.setPlainText(data.get("bio", ""))
            
            # Đặt QComboBox
            gender = data.get("gender", "other")
            index = self.gender_input.findText(gender, Qt.MatchFixedString)
            if index >= 0:
                self.gender_input.setCurrentIndex(index)
                
            # Đặt QDateEdit
            dob_str = data.get("date_of_birth")
            if dob_str:
                self.dob_input.setDate(QDate.fromString(dob_str, "yyyy-MM-dd"))
        else:
            QMessageBox.critical(self, "Lỗi", f"Không thể tải hồ sơ: {data.get('msg')}")
            self.reject()

    def save_profile(self):
        token = self.parent_app.token
        
        # Thu thập dữ liệu
        full_name = self.full_name_input.text().strip()
        gender = self.gender_input.currentText()
        dob = self.dob_input.date().toString("yyyy-MM-dd")
        bio = self.bio_input.toPlainText().strip()
        
        # Gọi API
        status, data = api_client.update_profile(
            token,
            full_name=full_name,
            gender=gender,
            date_of_birth=dob,
            bio=bio
        )

        if status == 200:
            QMessageBox.information(self, "Thành công", "Đã cập nhật hồ sơ.")
            self.accept() # Đóng dialog
        else:
            QMessageBox.warning(self, "Lỗi", f"Không thể cập nhật: {data.get('msg')}")