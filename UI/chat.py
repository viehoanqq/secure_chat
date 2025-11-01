from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel
from PyQt5.QtCore import Qt
import json
from services import api_client, crypto_client
from .home import sio

class ChatPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        header = QHBoxLayout()
        self.back_btn = QPushButton("Back")
        self.title_label = QLabel("Chat")
        self.title_label.setStyleSheet("font-size:16px;font-weight:bold")
        header.addWidget(self.back_btn)
        header.addWidget(self.title_label)
        header.addStretch()
        layout.addLayout(header)

        self.messages = QTextEdit()
        self.messages.setReadOnly(True)
        layout.addWidget(self.messages)

        bottom = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("Type a message...")
        self.send_btn = QPushButton("Send")
        bottom.addWidget(self.input)
        bottom.addWidget(self.send_btn)
        layout.addLayout(bottom)

        self.setLayout(layout)
        self.send_btn.clicked.connect(self.send)
        self.back_btn.clicked.connect(self.leave_room)

    # =====================================================
    # =============== LOAD & JOIN ROOM ====================
    # =====================================================
    def load_chat(self, chat_id):
        self.parent.current_chat_id = chat_id
        try:
            sio.emit("join_chat", {"chat_id": chat_id, "user_id": self.parent.user_id})
            print(f"[Socket] Joined room {chat_id}")
        except Exception as e:
            print(f"[Socket] join_chat failed: {e}")

        status, chat = api_client.get_chat_detail(self.parent.token, chat_id)
        if status == 200:
            self.title_label.setText(f"[{chat_id}] {chat['name']}")
        else:
            self.title_label.setText(f"Chat {chat_id}")

        # Load messages
        status, msgs = api_client.get_messages(self.parent.token, chat_id)
        self.messages.clear()
        if status == 200:
            for msg in msgs:
                is_me = msg['sender_id'] == self.parent.user_id
                try:
                    key_dict = json.loads(msg['aes_key_encrypted'])
                    wrapped = key_dict.get(str(self.parent.user_id))
                    if wrapped:
                        aes_key = crypto_client.unwrap_aes_key(wrapped, self.parent.private_key)
                        text = crypto_client.decrypt_aes_gcm(msg['content'], aes_key, msg['iv'], msg['tag'])
                    else:
                        text = "[No key]"
                except Exception as e:
                    text = f"[Error: {e}]"
                self.add_message(msg['sender_id'], text, is_me)

    def leave_room(self):
        try:
            sio.emit("leave_chat", {"chat_id": self.parent.current_chat_id, "user_id": self.parent.user_id})
            print(f"[Socket] Left room {self.parent.current_chat_id}")
        except:
            pass
        self.parent.layout.setCurrentWidget(self.parent.home_page)

    # =====================================================
    # ================= SEND MESSAGE ======================
    # =====================================================
    def send(self):
        text = self.input.text().strip()
        if not text:
            return

        chat_id = self.parent.current_chat_id
        status, chat = api_client.get_chat_detail(self.parent.token, chat_id)
        if status != 200:
            self.add_message("System", "Cannot get chat info", False)
            return

        aes_key = crypto_client.generate_aes_key()
        enc = crypto_client.encrypt_aes_gcm(text, aes_key)
        wrapped_keys = {}
        for mid in chat["members"]:
            s, info = api_client.get_user_info(self.parent.token, mid)
            if s == 200:
                wrapped = crypto_client.wrap_aes_key(aes_key, info["public_key"])
                wrapped_keys[str(mid)] = wrapped

        payload = {
            "chat_id": chat_id,
            "sender_id": self.parent.user_id,
            "content": enc["ciphertext"],
            "aes_key_encrypted": wrapped_keys,
            "iv": enc["iv"],
            "tag": enc["tag"]
        }
        sio.emit("send_message", payload)
        self.add_message(self.parent.user_id, text, True)
        self.input.clear()

    # =====================================================
    # ================= DISPLAY MESSAGE ===================
    # =====================================================
    def add_message(self, sender_id, text, is_me):
        align = "right" if is_me else "left"
        sender = "You" if is_me else f"User {sender_id}"
        html = f"""
        <div style="text-align:{align};margin:4px;">
            <div style='display:inline-block;padding:8px 14px;
                background:{'#0088cc' if is_me else '#333'};
                color:white;border-radius:12px;max-width:70%;'>
                <b>{sender}:</b> {text}
            </div>
        </div>
        """
        self.messages.append(html)
        self.messages.ensureCursorVisible()
