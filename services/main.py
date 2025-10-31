import sys, os, threading, time, json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PyQt5.QtWidgets import (
    QApplication, QWidget, QStackedLayout, QVBoxLayout,
    QPushButton, QLineEdit, QLabel, QListWidget, QTextEdit
)
from PyQt5.QtCore import Qt
from . import api_client, crypto_client
import socketio

BASE_URL = "http://127.0.0.1:5000"
SOCKET_URL = "http://127.0.0.1:5001"
sio = socketio.Client(reconnection=True, reconnection_attempts=5, reconnection_delay=1)


class ChatApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python Secure Chat")
        self.setGeometry(300, 100, 600, 600)

        self.token = None
        self.user_id = None
        self.private_key = None
        self.current_chat_id = None
        self.socket_connected = False

        self.layout = QStackedLayout()
        self.setLayout(self.layout)

        self.login_widget = self.build_login()
        self.chat_list_widget = self.build_chat_list()
        self.chat_room_widget = self.build_chat_room()

        self.layout.addWidget(self.login_widget)
        self.layout.addWidget(self.chat_list_widget)
        self.layout.addWidget(self.chat_room_widget)

    # ==========================================================
    # LOGIN / REGISTER
    # ==========================================================
    def build_login(self):
        widget = QWidget()
        layout = QVBoxLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_btn = QPushButton("Login")
        self.register_btn = QPushButton("Register")
        self.login_msg = QLabel("")

        self.login_btn.clicked.connect(self.do_login)
        self.register_btn.clicked.connect(self.do_register)

        layout.addWidget(QLabel("<h3>Login or Register</h3>"))
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_btn)
        layout.addWidget(self.register_btn)
        layout.addWidget(self.login_msg)
        widget.setLayout(layout)
        return widget

    def do_register(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        try:
            crypto_client.register_and_save_key(username, password)
            self.login_msg.setText("Register success! Please login.")
        except Exception as e:
            self.login_msg.setText(f"Register failed: {e}")

    def do_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        token, user_id, status, data = api_client.login(username, password)

        if status == 200:
            try:
                self.private_key = crypto_client.load_private_key(username, password)
            except Exception as e:
                self.login_msg.setText(f"Failed to load private key: {e}")
                return

            self.token = token
            self.user_id = user_id
            self.login_msg.setText("Login success!")
            threading.Thread(target=self.connect_socket, daemon=True).start()
            self.refresh_chat_list()
            self.layout.setCurrentWidget(self.chat_list_widget)
        else:
            self.login_msg.setText(data.get("msg", "Login failed"))

    # ==========================================================
    # CHAT LIST
    # ==========================================================
    def build_chat_list(self):
        widget = QWidget()
        layout = QVBoxLayout()

        self.chat_list_widget_ui = QListWidget()
        self.chat_list_widget_ui.itemClicked.connect(self.open_chat_room)

        self.online_list_widget = QListWidget()
        self.online_list_widget.itemClicked.connect(self.start_chat_with_user)

        self.refresh_btn = QPushButton("Refresh Chats")
        self.logout_btn = QPushButton("Logout")

        self.refresh_btn.clicked.connect(self.refresh_chat_list)
        self.logout_btn.clicked.connect(self.do_logout)

        layout.addWidget(QLabel("<b>Your Chats</b>"))
        layout.addWidget(self.chat_list_widget_ui)
        layout.addWidget(self.refresh_btn)
        layout.addWidget(QLabel("<b>Online Users</b>"))
        layout.addWidget(self.online_list_widget)
        layout.addWidget(self.logout_btn)

        widget.setLayout(layout)
        return widget

    def refresh_chat_list(self):
        status, chats = api_client.get_chats(self.token)
        self.chat_list_widget_ui.clear()
        if status == 200:
            for chat in chats:
                text = f"{chat['chat_id']}: {chat['name']} ({'Group' if chat['is_group'] else '1-1'})"
                self.chat_list_widget_ui.addItem(text)

    def open_chat_room(self, item):
        chat_id = int(item.text().split(":")[0])
        self.current_chat_id = chat_id

        if not self.socket_connected:
            self.chat_text.append("[System] Đang kết nối...")
            for _ in range(50):
                if self.socket_connected: break
                time.sleep(0.1)
            else:
                self.chat_text.append("[Error] Không thể kết nối.")
                return

        self.layout.setCurrentWidget(self.chat_room_widget)
        sio.emit("join_chat", {"chat_id": chat_id, "user_id": self.user_id})
        self.load_chat_messages(chat_id)

    def start_chat_with_user(self, item):
        user_id = int(item.text().split(":")[0])
        status, chat = api_client.create_chat(
            self.token, name=f"Chat with {user_id}", is_group=False, members=[user_id]
        )
        if status in (200, 201):
            self.current_chat_id = chat["chat_id"]
            self.layout.setCurrentWidget(self.chat_room_widget)
            sio.emit("join_chat", {"chat_id": self.current_chat_id, "user_id": self.user_id})
            self.load_chat_messages(self.current_chat_id)

    # ==========================================================
    # CHAT ROOM
    # ==========================================================
    def build_chat_room(self):
        widget = QWidget()
        layout = QVBoxLayout()

        self.chat_text = QTextEdit()
        self.chat_text.setReadOnly(True)
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Enter your message...")
        self.send_btn = QPushButton("Send")
        self.back_btn = QPushButton("Back")

        self.send_btn.clicked.connect(self.send_message)
        self.back_btn.clicked.connect(lambda: self.layout.setCurrentWidget(self.chat_list_widget))

        layout.addWidget(QLabel("<b>Chat Room</b>"))
        layout.addWidget(self.chat_text)
        layout.addWidget(self.message_input)
        layout.addWidget(self.send_btn)
        layout.addWidget(self.back_btn)
        widget.setLayout(layout)
        return widget

    def scroll_to_bottom(self):
        sb = self.chat_text.verticalScrollBar()
        sb.setValue(sb.maximum())

    def load_chat_messages(self, chat_id):
        status, messages = api_client.get_messages(self.token, chat_id)
        self.chat_text.clear()
        if status == 200:
            for msg in messages:
                sender = msg['sender_id']
                try:
                    # ĐỌC TỪ DB: aes_key_encrypted là JSON string
                    key_dict = json.loads(msg['aes_key_encrypted'])
                    wrapped = key_dict.get(str(self.user_id))
                    if not wrapped:
                        plaintext = "[No key for you]"
                    else:
                        aes_key = crypto_client.unwrap_aes_key(wrapped, self.private_key)
                        plaintext = crypto_client.decrypt_aes_gcm(
                            msg['content'], aes_key, msg['iv'], msg['tag']
                        )
                except Exception as e:
                    plaintext = f"[Cannot decrypt: {e}]"
                self.chat_text.append(f"{sender}: {plaintext}")
        self.scroll_to_bottom()

    def send_message(self):
        content = self.message_input.text().strip()
        if not content or not self.socket_connected:
            return

        status, chat = api_client.get_chat_detail(self.token, self.current_chat_id)
        if status != 200:
            self.chat_text.append("[Error] Cannot get chat members")
            return

        aes_key = crypto_client.generate_aes_key()
        enc = crypto_client.encrypt_aes_gcm(content, aes_key)
        wrapped_keys = {}

        # BỌC KEY CHO TẤT CẢ THÀNH VIÊN, BAO GỒM CHÍNH MÌNH
        for member_id in chat["members"]:
            s, user_info = api_client.get_user_info(self.token, member_id)
            if s != 200:
                continue
            pub_key = user_info["public_key"]
            wrapped = crypto_client.wrap_aes_key(aes_key, pub_key)
            wrapped_keys[str(member_id)] = wrapped  # BAO GỒM CẢ NGƯỜI GỬI

        payload = {
            "chat_id": self.current_chat_id,
            "sender_id": self.user_id,
            "content": enc["ciphertext"],
            "aes_key_encrypted": wrapped_keys,  # CÓ KEY CHO MỌI NGƯỜI
            "iv": enc["iv"],
            "tag": enc["tag"]
        }
        sio.emit("send_message", payload)
        self.chat_text.append(f"You: {content}")
        self.message_input.clear()
        self.scroll_to_bottom()

    # ==========================================================
    # SOCKET.IO
    # ==========================================================
    def connect_socket(self):
        def _connect():
            try:
                sio.connect(SOCKET_URL, auth={"token": self.token}, wait=True, wait_timeout=10)
                self.socket_connected = True
                print("[Socket] Connected")
            except Exception as e:
                print(f"[Socket] Failed: {e}")

        threading.Thread(target=_connect, daemon=True).start()

        @sio.on("connect")
        def on_connect():
            self.socket_connected = True
            print("[Socket] Connected")

        @sio.on("disconnect")
        def on_disconnect():
            self.socket_connected = False
            print("[Socket] Disconnected")

        @sio.on("receive_message")
        def on_receive(msg):
            if msg["chat_id"] != self.current_chat_id:
                return
            try:
                key_dict = msg['aes_key_encrypted']
                if not isinstance(key_dict, dict):
                    raise ValueError("Invalid aes_key_encrypted format")
                wrapped = key_dict.get(str(self.user_id))
                if not wrapped:
                    plaintext = "[No key for you]"
                else:
                    aes_key = crypto_client.unwrap_aes_key(wrapped, self.private_key)
                    plaintext = crypto_client.decrypt_aes_gcm(
                        msg['content'], aes_key, msg['iv'], msg['tag']
                    )
            except Exception as e:
                plaintext = f"[Cannot decrypt: {e}]"
                print(f"[Debug] Decrypt failed: {e}, key_dict={key_dict}")
            self.chat_text.append(f"{msg['sender_id']}: {plaintext}")
            self.scroll_to_bottom()

        @sio.on("online_users")
        def on_online(users):
            self.online_list_widget.clear()
            for uid in users:
                if uid != self.user_id:
                    self.online_list_widget.addItem(f"{uid}: User{uid}")

    # ==========================================================
    # LOGOUT
    # ==========================================================
    def do_logout(self):
        try:
            sio.disconnect()
        except: pass
        api_client.logout(self.token)
        self.token = self.user_id = self.private_key = None
        self.socket_connected = False
        self.layout.setCurrentWidget(self.login_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatApp()
    window.show()
    sys.exit(app.exec_())