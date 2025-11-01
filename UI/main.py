# main.py
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QStackedLayout
from PyQt5.QtCore import Qt
from .login import LoginPage
from .home import HomePage
from .register import RegisterPage # <--- THÊM IMPORT

class ChatApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SecureChat")
        self.resize(1100, 700)
        self.setMinimumSize(900, 600)

        # Trạng thái toàn cục của ứng dụng
        self.token = None
        self.user_id = None
        self.private_key = None
        
        self.layout = QStackedLayout()
        self.setLayout(self.layout)

        self.login_page = LoginPage(self)
        self.home_page = HomePage(self)
        self.register_page = RegisterPage(self) # <--- TẠO INSTANCE

        self.layout.addWidget(self.login_page)
        self.layout.addWidget(self.home_page)
        self.layout.addWidget(self.register_page) # <--- THÊM VÀO STACK

        self.layout.setCurrentWidget(self.login_page)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion") # Fusion style hoạt động tốt với QSS tùy chỉnh
    window = ChatApp()
    window.show()
    sys.exit(app.exec_())