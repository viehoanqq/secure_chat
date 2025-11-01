from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QPushButton, QLabel, QFrame, QListWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from services import api_client, crypto_client
import socketio, threading

SOCKET_URL = "http://127.0.0.1:5001"
sio = socketio.Client(reconnection=True)

class HomePage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.online_users = {}
        self.socket_connected = False
        self._socket_initialized = False
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QListWidget {
                background-color: #f4f6f8;
                border: none;
                color: #222;
                outline: none;
            }
            QListWidget::item {
                padding: 8px;
                border: none;
                border-radius: 8px;
                background-color: #ffffff;
                margin: 4px 0;
            }
            QListWidget::item:hover { 
                background-color: #e9f5ff;
            }
            QListWidget::item:selected { 
                background-color: #d0ebff;
                color: #0a3d62;
            }
            QPushButton {
                background-color: #0088cc;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 16px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover { 
                background-color: #0099ee;
            }
            QPushButton:pressed {
                background-color: #0077bb;
            }
            QFrame {
                background-color: #ffffff;
            }
        """)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ===== SIDEBAR =====
        sidebar = QFrame()
        sidebar.setFixedWidth(340)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-right: 1px solid #dee2e6;
            }
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(16, 16, 16, 16)
        sidebar_layout.setSpacing(12)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("💬 SecureChat")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setWeight(QFont.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: #0088cc;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        sidebar_layout.addLayout(header_layout)

        sep1 = QFrame()
        sep1.setStyleSheet("background-color: #dee2e6;")
        sep1.setFixedHeight(1)
        sidebar_layout.addWidget(sep1)

        # Chats Section
        chats_label = QLabel("Active Chats")
        chats_font = QFont()
        chats_font.setPointSize(11)
        chats_font.setWeight(QFont.Bold)
        chats_label.setFont(chats_font)
        chats_label.setStyleSheet("color: #333; margin-top: 8px;")
        sidebar_layout.addWidget(chats_label)

        self.chat_list = QListWidget()
        sidebar_layout.addWidget(self.chat_list, 1)

        self.chat_list.itemClicked.connect(self.on_chat_clicked)

        sep2 = QFrame()
        sep2.setStyleSheet("background-color: #dee2e6;")
        sep2.setFixedHeight(1)
        sidebar_layout.addWidget(sep2)

        # Online Users
        online_label = QLabel("Online Users")
        online_font = QFont()
        online_font.setPointSize(11)
        online_font.setWeight(QFont.Bold)
        online_label.setFont(online_font)
        online_label.setStyleSheet("color: #2f9e44; margin-top: 8px;")
        sidebar_layout.addWidget(online_label)

        self.online_list = QListWidget()
        sidebar_layout.addWidget(self.online_list, 1)

        self.online_list.itemClicked.connect(self.start_chat_with_user)

        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        self.refresh_btn = QPushButton("Refresh")
        self.logout_btn = QPushButton("Logout")
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addWidget(self.logout_btn)
        sidebar_layout.addLayout(btn_layout)

        main_layout.addWidget(sidebar)

        # ===== MAIN CONTENT =====
        self.placeholder = QLabel("Select a chat to start messaging")
        placeholder_font = QFont()
        placeholder_font.setPointSize(16)
        self.placeholder.setFont(placeholder_font)
        self.placeholder.setStyleSheet("color: #777; background-color: #f4f6f8;")
        self.placeholder.setAlignment(Qt.AlignCenter)
        
        # main_layout.addWidget(self.placeholder, 1)

        # Tạo ChatPage (được ẩn ban đầu)
        from .chat import ChatPage
        self.chat_page = ChatPage(self.parent)
        self.chat_page.hide()

        # Widget trung tâm: chứa cả placeholder và chat_page
        self.content_frame = QFrame()
        content_layout = QVBoxLayout(self.content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(self.placeholder)
        content_layout.addWidget(self.chat_page)
        main_layout.addWidget(self.content_frame, 1)


        self.refresh_btn.clicked.connect(self.refresh_chats)
        self.logout_btn.clicked.connect(self.logout)

    # ===== SOCKET / LOGIC =====
    def connect_socket(self):
        if self._socket_initialized: 
            return
        self._socket_initialized = True

        def _connect():
            try:
                sio.connect(SOCKET_URL, auth={"token": self.parent.token}, wait_timeout=10)
                self.socket_connected = True
                print("[Socket] Connected")
            except Exception as e:
                print(f"[Socket] Connect error: {e}")

        threading.Thread(target=_connect, daemon=True).start()

        @sio.on("connect")
        def on_connect():
            self.socket_connected = True
            print("[Socket] Connected")

        @sio.on("disconnect")
        def on_disconnect():
            self.socket_connected = False
            print("[Socket] Disconnected")

        @sio.on("online_users")
        def on_online(users):
            self.online_users = {uid: True for uid in users if uid != self.parent.user_id}
            self.update_online_list()

        @sio.on("receive_message")
        def on_receive(msg):
            chat_id = msg["chat_id"]
            sender = msg["sender_id"]
            try:
                key_dict = msg["aes_key_encrypted"]
                wrapped = key_dict.get(str(self.parent.user_id))
                if wrapped:
                    aes_key = crypto_client.unwrap_aes_key(wrapped, self.parent.private_key)
                    text = crypto_client.decrypt_aes_gcm(msg["content"], aes_key, msg["iv"], msg["tag"])
                else:
                    text = "[No key]"
            except Exception as e:
                text = f"[Decrypt error: {e}]"
            if self.parent.layout.currentWidget() == self.parent.chat_page and self.parent.current_chat_id == chat_id:
                self.parent.chat_page.add_message(sender, text, sender == self.parent.user_id)
            else:
                print(f"[New Msg] in chat {chat_id}")
                self.refresh_chats()

    def update_online_list(self):
        self.online_list.clear()
        for uid in self.online_users.keys():
            item = QListWidgetItem(f"🟢 User {uid}")
            item.setData(Qt.UserRole, uid)
            item.setForeground(QColor("#2f9e44"))
            self.online_list.addItem(item)

    def refresh_chats(self):
        status, chats = api_client.get_chats(self.parent.token)
        self.chat_list.clear()
        if status == 200:
            for c in chats:
                text = f"{c['name']}"
                item = QListWidgetItem(text)
                item.setData(Qt.UserRole, c["chat_id"])
                self.chat_list.addItem(item)

    def on_chat_clicked(self, item):
        # chat_id = item.data(Qt.UserRole)
        # self.parent.chat_page.load_chat(chat_id)
        # self.parent.layout.setCurrentWidget(self.parent.chat_page)

        chat_id = item.data(Qt.UserRole)
        # Ẩn placeholder, hiện chat_page
        self.placeholder.hide()
        self.chat_page.show()
        self.chat_page.load_chat(chat_id)
        # Lưu trạng thái hiện tại
        self.parent.current_chat_id = chat_id

    def start_chat_with_user(self, item):
        uid = item.data(Qt.UserRole)
        if uid == self.parent.user_id:
            return
        status, chat = api_client.create_chat(
            self.parent.token, 
            name=f"Chat with {uid}", 
            is_group=False, 
            members=[uid]
        )
        if status in (200, 201):
            self.parent.chat_page.load_chat(chat["chat_id"])
            self.parent.layout.setCurrentWidget(self.parent.chat_page)

    def logout(self):
        try: 
            sio.disconnect()
        except: 
            pass
        api_client.logout(self.parent.token)
        self.parent.layout.setCurrentWidget(self.parent.login_page)
