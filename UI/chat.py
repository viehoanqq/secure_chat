from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel, QScrollArea
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QFont, QColor, QIcon, QPixmap, QPainter, QPainterPath
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve
import json
from services import api_client, crypto_client
from .home import sio

class ChatPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        header = QHBoxLayout()
        header.setContentsMargins(16, 12, 16, 12)
        header.setSpacing(12)
        
        # Back button with icon
        self.back_btn = QPushButton("←")
        self.back_btn.setFixedSize(40, 40)
        self.back_btn.setFont(QFont("Arial", 16, QFont.Bold))
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: #f0f2f5;
                border: none;
                border-radius: 8px;
                color: #0088cc;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e4e6eb;
            }
            QPushButton:pressed {
                background-color: #d0d2d7;
            }
        """)
        
        # Title label with better styling
        self.title_label = QLabel("Chat")
        title_font = QFont("Segoe UI", 15, QFont.Bold)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet("color: #000; margin: 0px;")
        
        # Subtitle for online status
        self.status_label = QLabel("Online")
        status_font = QFont("Segoe UI", 11)
        status_font.setWeight(QFont.Normal)
        self.status_label.setFont(status_font)
        self.status_label.setStyleSheet("color: #65676b; margin: 0px;")
        
        # Title and status column
        title_layout = QVBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(2)
        title_layout.addWidget(self.title_label)
        title_layout.addWidget(self.status_label)
        
        header.addWidget(self.back_btn)
        header.addLayout(title_layout)
        header.addStretch()
        
        # Header container with background
        header_widget = QWidget()
        header_widget.setLayout(header)
        header_widget.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border-bottom: 1px solid #e5e7eb;
            }
        """)
        main_layout.addWidget(header_widget)

        messages_container = QWidget()
        messages_layout = QVBoxLayout()
        messages_layout.setContentsMargins(0, 0, 0, 0)
        messages_layout.setSpacing(0)
        
        self.messages = QTextEdit()
        self.messages.setReadOnly(True)
        self.messages.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff;
                border: none;
                padding: 16px;
                font-family: 'Segoe UI', Arial;
                font-size: 13px;
                color: #000;
            }
        """)
        messages_layout.addWidget(self.messages)
        messages_container.setLayout(messages_layout)
        main_layout.addWidget(messages_container, 1)

        input_container = QWidget()
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(12, 12, 12, 12)
        input_layout.setSpacing(8)
        
        # Input field
        self.input = QLineEdit()
        self.input.setPlaceholderText("Aa")
        self.input.setMinimumHeight(40)
        self.input.setStyleSheet("""
            QLineEdit {
                background-color: #f0f2f5;
                border: 1px solid #ccc;
                padding: 8px 16px;
                font-size: 13px;
                color: #000;
            }
            QLineEdit:focus {
                background-color: #fff;
                border: 2px solid #0088cc;
                padding: 7px 15px;
            }
            QLineEdit::placeholder {
                color: #65676b;
            }
        """)
        
        # Send button with icon
        self.send_btn = QPushButton("Send")
        self.send_btn.setMinimumHeight(40)
        self.send_btn.setFixedWidth(70)
        self.send_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #0088cc;
                color: white;
                border: none;
                border-radius: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0073b1;
            }
            QPushButton:pressed {
                background-color: #005a96;
            }
        """)
        
        input_layout.addWidget(self.input)
        input_layout.addWidget(self.send_btn)
        
        input_container.setLayout(input_layout)
        input_container.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border-top: 1px solid #e5e7eb;
            }
        """)
        main_layout.addWidget(input_container)

        self.setLayout(main_layout)
        self.send_btn.clicked.connect(self.send)
        self.back_btn.clicked.connect(self.leave_room)

    def load_chat(self, chat_id):
        self.parent.current_chat_id = chat_id
        try:
            sio.emit("join_chat", {"chat_id": chat_id, "user_id": self.parent.user_id})
            print(f"[Socket] Joined room {chat_id}")
        except Exception as e:
            print(f"[Socket] join_chat failed: {e}")

        status, chat = api_client.get_chat_detail(self.parent.token, chat_id)
        if status == 200:
            self.title_label.setText(chat.get('name', f'Chat {chat_id}'))
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
        # Ẩn chat page, hiện lại danh sách
        self.hide()
        self.parent.home_page.placeholder.show()

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

    def add_message(self, sender_id, text, is_me):
        sender = "You" if is_me else f"User {sender_id}"
        
        if is_me:
            # User's message - right aligned with blue bubble
            html = f"""
            <div style="text-align: right; margin: 8px 0px; padding-right: 8px;">
                <div style="display: inline-block; max-width: 70%; padding: 10px 14px; 
                    background: linear-gradient(135deg, #0088cc 0%, #0070b3 100%);
                    color: green; border-radius: 18px; box-shadow: 0 1px 2px rgba(0,0,0,0.1);
                    word-wrap: break-word; text-align: left;">
                    <span style="font-size: 13px;">{text}</span>
                </div>
            </div>
            """
        else:
            # Other user's message - left aligned with gray bubble
            html = f"""
            <div style="text-align: left; margin: 8px 0px; padding-left: 8px;">
                <div style="display: inline-block; max-width: 70%; padding: 10px 14px;
                    background-color: #f0f2f5; color: #000; border-radius: 18px; 
                    box-shadow: 0 1px 2px rgba(0,0,0,0.05); word-wrap: break-word; text-align: left;">
                    <span style="font-weight: bold; font-size: 12px; color: #0088cc;">{sender}</span><br>
                    <span style="font-size: 13px;">{text}</span>
                </div>
            </div>
            """
        
        self.messages.append(html)
        self.messages.ensureCursorVisible()