# UI/chat.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel, QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import json
from services import api_client, crypto_client

class ChatPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent 
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', 'Inter', sans-serif;
                background-color: #ffffff;
            }
            
            /* ===== HEADER ===== */
            QFrame#header {
                background-color: #ffffff;
                border-bottom: 1px solid #e7e7e7;
            }
            QLabel#avatar {
                font-size: 24px;
                padding: 5px;
            }
            QLabel#title {
                color: #111;
                font-size: 16px;
                font-weight: 600;
            }
            QLabel#status {
                color: #0088cc;
                font-size: 13px;
            }
            QLabel#status[status="offline"] {
                color: #777;
            }
            QPushButton.action_btn {
                font-size: 18px;
                font-weight: 600;
                color: #777;
                border: none;
                background: transparent;
                padding: 8px;
                border-radius: 8px;
            }
            QPushButton.action_btn:hover {
                background-color: #f0f2f5;
                color: #111;
            }
            
            /* ===== KHUNG CHAT ===== */
            QTextEdit#messages {
                background-color: #ffffff;
                border: none;
                padding: 10px;
                color: #111;
                font-size: 14px; /* <--- Sửa font-size chung */
            }
            
            /* ===== KHUNG NHẬP LIỆU ===== */
            QFrame#input_frame {
                background-color: #f7f9fa;
                border-top: 1px solid #e7e7e7;
                padding: 10px 15px;
            }
            QFrame#input_bg {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 20px;
            }
            QFrame#input_bg:focus-within {
                 border: 1px solid #0088cc;
            }
            QLineEdit#input {
                background-color: transparent;
                border: none;
                padding: 10px 15px;
                font-size: 14px;
                color: #111;
            }
            QPushButton#send_btn {
                font-size: 20px;
                font-weight: 700;
                color: #0088cc;
                padding-right: 10px;
            }
            QPushButton#attach_btn {
                font-size: 20px;
                font-weight: 700;
                color: #777;
                padding-left: 10px;
            }
            QPushButton#attach_btn:hover { color: #111; }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ===== HEADER =====
        header_frame = QFrame()
        header_frame.setObjectName("header")
        header_frame.setFixedHeight(60)
        header = QHBoxLayout(header_frame)
        header.setContentsMargins(15, 0, 15, 0)
        header.setSpacing(10)
        
        self.avatar_label = QLabel("👤")
        self.avatar_label.setObjectName("avatar")
        
        title_layout = QVBoxLayout()
        title_layout.setSpacing(0)
        title_layout.setContentsMargins(0, 0, 0, 0)
        self.title_label = QLabel("Tên Chat")
        self.title_label.setObjectName("title")
        self.status_label = QLabel("...")
        self.status_label.setObjectName("status")
        title_layout.addWidget(self.title_label)
        title_layout.addWidget(self.status_label)
        
        self.call_button = QPushButton("📞")
        self.call_button.setObjectName("action_btn")
        self.call_button.setCursor(Qt.PointingHandCursor)
        self.video_button = QPushButton("📹")
        self.video_button.setObjectName("action_btn")
        self.video_button.setCursor(Qt.PointingHandCursor)
        self.info_button = QPushButton("ℹ️")
        self.info_button.setObjectName("action_btn")
        self.info_button.setCursor(Qt.PointingHandCursor)

        header.addWidget(self.avatar_label)
        header.addLayout(title_layout)
        header.addStretch()
        header.addWidget(self.call_button)
        header.addWidget(self.video_button)
        header.addWidget(self.info_button)
        main_layout.addWidget(header_frame)

        # ===== KHUNG CHAT =====
        self.messages = QTextEdit()
        self.messages.setObjectName("messages")
        self.messages.setReadOnly(True)
        main_layout.addWidget(self.messages, 1)

        # ===== KHUNG NHẬP LIỆU =====
        input_container = QFrame()
        input_container.setObjectName("input_frame")
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        
        input_bg = QFrame() 
        input_bg.setObjectName("input_bg")
        input_bg_layout = QHBoxLayout(input_bg)
        input_bg_layout.setContentsMargins(0, 0, 0, 0)
        input_bg_layout.setSpacing(5)

        self.attach_btn = QPushButton("📎")
        self.attach_btn.setObjectName("attach_btn")
        self.attach_btn.setCursor(Qt.PointingHandCursor)
        
        self.input = QLineEdit()
        self.input.setObjectName("input")
        self.input.setPlaceholderText("Nhập tin nhắn...")
        
        self.send_btn = QPushButton("➤")
        self.send_btn.setObjectName("send_btn")
        self.send_btn.setCursor(Qt.PointingHandCursor)
        
        input_bg_layout.addWidget(self.attach_btn)
        input_bg_layout.addWidget(self.input, 1)
        input_bg_layout.addWidget(self.send_btn)
        
        input_layout.addWidget(input_bg)
        main_layout.addWidget(input_container)

        self.setLayout(main_layout)
        
        self.send_btn.clicked.connect(self.send)
        self.input.returnPressed.connect(self.send)

    def clear_chat(self):
        self.messages.clear()
        self.input.clear()
        self.title_label.setText("Chat")
        self.status_label.setText("...")
        
    def load_chat(self, chat_id):
        from .home import sio 
        
        token = self.parent.parent.token
        user_id = self.parent.parent.user_id
        private_key = self.parent.parent.private_key
        
        socket_was_connected = True 

        if not sio.connected:
            socket_was_connected = False
            print("[Socket] Lỗi (join_chat): sio.connected is False...")
            try:
                self.parent.connect_socket() 
            except Exception as e:
                print(f"[Socket] Lỗi khi kết nối lại: {e}")
        else:
            try:
                sio.emit("join_chat", {"chat_id": chat_id, "user_id": user_id})
                print(f"[Socket] Đã tham gia phòng {chat_id}")
            except Exception as e:
                print(f"[Socket] Lỗi join_chat (dù đã connected?): {e}")
                socket_was_connected = False

        status, chat = api_client.get_chat_detail(token, chat_id)
        if status == 200:
            self.title_label.setText(chat.get('name', f'Chat {chat_id}'))
            
            other_user_id = None
            if not chat.get('is_group') and len(chat.get('members', [])) == 2:
                other_user_id = next((uid for uid in chat['members'] if uid != user_id), None)
            
            self.parent.current_other_user_id = other_user_id
            
            if other_user_id:
                stat, data = api_client.get_user_info(token, other_user_id)
                if stat == 200:
                    status_text = data.get('status', 'offline')
                    self.status_label.setText(status_text)
                    self.status_label.setProperty("status", status_text)
                else:
                    self.status_label.setText("không rõ")
                    self.status_label.setProperty("status", "offline")
            else:
                self.status_label.setText(f"{len(chat.get('members',[]))} thành viên")
                self.status_label.setProperty("status", "online") 
            
            self.status_label.style().unpolish(self.status_label)
            self.status_label.style().polish(self.status_label)

        else:
            self.title_label.setText(f"Chat {chat_id}")
            self.status_label.setText("Không thể tải")

        status, msgs = api_client.get_messages(token, chat_id)
        self.messages.clear() 

        if not socket_was_connected:
            self.add_message("System", "Không thể kết nối real-time. Đang hiển thị lịch sử trò chuyện.", False)
        
        if status != 200:
             self.add_message("System", "Không thể tải lịch sử tin nhắn.", False)

        if status == 200:
            for msg in msgs:
                is_me = msg['sender_id'] == user_id
                try:
                    key_dict = json.loads(msg['aes_key_encrypted'])
                    wrapped = key_dict.get(str(user_id))
                    if wrapped:
                        aes_key = crypto_client.unwrap_aes_key(wrapped, private_key)
                        text = crypto_client.decrypt_aes_gcm(msg['content'], aes_key, msg['iv'], msg['tag'])
                    else:
                        text = "[Không có khóa]"
                except Exception as e:
                    text = f"[Lỗi giải mã: {e}]"
                self.add_message(msg['sender_id'], text, is_me)

    def send(self):
        from .home import sio 
        
        text = self.input.text().strip()
        if not text:
            return

        token = self.parent.parent.token
        user_id = self.parent.parent.user_id
        chat_id = self.parent.current_chat_id 

        if not chat_id:
            self.add_message("System", "Lỗi: Không có chat_id", False)
            return
            
        if not sio.connected:
            print("[Socket] Lỗi (send): sio.connected is False...")
            self.add_message("System", "Lỗi: Mất kết nối. Đang thử kết nối lại...", False)
            try:
                self.parent.connect_socket() 
            except Exception as e:
                print(f"[Socket] Lỗi khi kết nối lại: {e}")
            return 

        status, chat = api_client.get_chat_detail(token, chat_id)
        if status != 200:
            self.add_message("System", "Không thể lấy thông tin chat để gửi", False)
            return

        aes_key = crypto_client.generate_aes_key()
        enc = crypto_client.encrypt_aes_gcm(text, aes_key)
        wrapped_keys = {}
        for mid in chat["members"]:
            s, info = api_client.get_user_info(token, mid)
            if s == 200:
                wrapped = crypto_client.wrap_aes_key(aes_key, info["public_key"])
                wrapped_keys[str(mid)] = wrapped
            else:
                print(f"Không thể lấy pubkey cho user {mid}")

        if not wrapped_keys:
             self.add_message("System", "Lỗi: Không thể mã hóa khóa cho người nhận", False)
             return

        payload = {
            "chat_id": chat_id,
            "sender_id": user_id,
            "content": enc["ciphertext"],
            "aes_key_encrypted": wrapped_keys,
            "iv": enc["iv"],
            "tag": enc["tag"]
        }
        
        try:
            sio.emit("send_message", payload)
            self.input.clear()
        except Exception as e:
            print(f"[Socket] Lỗi send_message: {e}")
            self.add_message("System", f"Lỗi gửi tin: {e}", False)

    def add_message(self, sender_id, text, is_me):
        # <--- SỬA ĐỔI: XÓA NỀN BONG BÓNG CHAT
        
        text = text.replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')
        
        if sender_id == "System":
            # Tin nhắn hệ thống (giữ nguyên style cũ, chỉ xóa nền)
            html = f"""
            <div style="text-align: center; margin: 8px 0; padding: 0 5px;">
                <span style="color: #777; font-size: 12px; font-style: italic;">
                    {text}
                </span>
            </div>
            """
        elif is_me:
            # Tin nhắn của bạn (bên phải, in đậm)
            html = f"""
            <div style="text-align: right; margin: 5px 0; padding-right: 10px;">
                <span style="color: #000; font-weight: 500; font-size: 14px; word-wrap: break-word;">{text}</span>
            </div>
            """
        else:
            # Tin nhắn của người khác (bên trái, chữ thường)
            html = f"""
            <div style="text-align: left; margin: 5px 0; padding-left: 10px;">
                <span style="color: #000; font-size: 14px; word-wrap: break-word;">{text}</span>
            </div>
            """
        
        self.messages.append(html)
        self.messages.verticalScrollBar().setValue(self.messages.verticalScrollBar().maximum())