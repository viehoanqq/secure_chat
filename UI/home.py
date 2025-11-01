from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QPushButton, QLabel, QFrame, QListWidgetItem
from PyQt5.QtCore import Qt
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
                background-color: #1a1a1a;
                border: none;
                color: white;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #2a2a2a;
            }
            QListWidget::item:hover { background-color: #2a2a2a; }
            QListWidget::item:selected { background-color: #0088cc; }
            QPushButton {
                background-color: #0088cc;
                color: white;
                border-radius: 8px;
                padding: 8px 12px;
            }
            QPushButton:hover { background-color: #0099ee; }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        sidebar = QFrame()
        sidebar.setFixedWidth(320)
        sidebar.setStyleSheet("background-color: #111; border-right: 1px solid #333;")
        sbl = QVBoxLayout(sidebar)
        sbl.setContentsMargins(10, 10, 10, 10)

        title = QLabel("SecureChat")
        title.setStyleSheet("color:#0088cc;font-size:20px;font-weight:bold;")
        sbl.addWidget(title)

        chats_label = QLabel("Chats")
        chats_label.setStyleSheet("color:#aaa;font-weight:bold;margin-top:15px;")
        sbl.addWidget(chats_label)

        self.chat_list = QListWidget()
        self.chat_list.itemClicked.connect(self.on_chat_clicked)
        sbl.addWidget(self.chat_list)

        online_label = QLabel("Online Users")
        online_label.setStyleSheet("color:#51cf66;font-weight:bold;margin-top:15px;")
        sbl.addWidget(online_label)

        self.online_list = QListWidget()
        self.online_list.itemClicked.connect(self.start_chat_with_user)
        sbl.addWidget(self.online_list)

        btns = QHBoxLayout()
        self.refresh_btn = QPushButton("Refresh")
        self.logout_btn = QPushButton("Logout")
        btns.addWidget(self.refresh_btn)
        btns.addWidget(self.logout_btn)
        sbl.addLayout(btns)

        layout.addWidget(sidebar)

        placeholder = QLabel("Select a chat to start messaging 💬")
        placeholder.setStyleSheet("color:#777;font-size:16px;")
        placeholder.setAlignment(Qt.AlignCenter)
        layout.addWidget(placeholder, 1)

        self.refresh_btn.clicked.connect(self.refresh_chats)
        self.logout_btn.clicked.connect(self.logout)

    # ===== Socket / Logic (unchanged) =====
    def connect_socket(self):
        if self._socket_initialized: return
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
            item = QListWidgetItem(f"User {uid}")
            item.setData(Qt.UserRole, uid)
            self.online_list.addItem(item)

    def refresh_chats(self):
        status, chats = api_client.get_chats(self.parent.token)
        self.chat_list.clear()
        if status == 200:
            for c in chats:
                text = f"[{c['chat_id']}] {c['name']}"
                item = QListWidgetItem(text)
                item.setData(Qt.UserRole, c["chat_id"])
                self.chat_list.addItem(item)

    def on_chat_clicked(self, item):
        chat_id = item.data(Qt.UserRole)
        self.parent.chat_page.load_chat(chat_id)
        self.parent.layout.setCurrentWidget(self.parent.chat_page)

    def start_chat_with_user(self, item):
        uid = item.data(Qt.UserRole)
        if uid == self.parent.user_id:
            return
        status, chat = api_client.create_chat(self.parent.token, name=f"Chat with {uid}", is_group=False, members=[uid])
        if status in (200, 201):
            self.parent.chat_page.load_chat(chat["chat_id"])
            self.parent.layout.setCurrentWidget(self.parent.chat_page)

    def logout(self):
        try: sio.disconnect()
        except: pass
        api_client.logout(self.parent.token)
        self.parent.layout.setCurrentWidget(self.parent.login_page)
