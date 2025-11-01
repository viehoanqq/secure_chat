# UI/home.py
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QListWidget, 
    QPushButton, QLabel, QFrame, QListWidgetItem, QLineEdit,
    QStackedLayout
)
# <--- THÊM IMPORT MỚI
from PyQt5.QtCore import Qt, QObject, pyqtSignal
# --->
from PyQt5.QtGui import QFont, QColor
from services import api_client, crypto_client
import socketio, threading

from .chat import ChatPage 
from .profile import ProfilePage
from .info_panel import InfoPanel 

SOCKET_URL = "http://127.0.0.1:5001"
sio = socketio.Client(reconnection=True)

# <--- LỚP MỚI ĐỂ XỬ LÝ TÍN HIỆU THREAD-SAFE
class SocketSignals(QObject):
    """
    Giữ các tín hiệu (signals) để giao tiếp
    an toàn từ thread socket về thread GUI.
    """
    connected = pyqtSignal()
    disconnected = pyqtSignal()
    online_users_received = pyqtSignal(list)
    new_message_received = pyqtSignal(dict)
# --->

class HomePage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent # parent là ChatApp
        self.online_users = {}
        self.socket_connected = False
        self._socket_initialized = False
        self.current_chat_id = None 
        self.current_other_user_id = None 
        
        # <--- KHỞI TẠO SIGNALS
        self.socket_signals = SocketSignals()
        # --->
        
        self.init_ui()
        
        # <--- KẾT NỐI SIGNALS VỚI CÁC HÀM (SLOTS)
        self.socket_signals.connected.connect(self.on_socket_connected)
        self.socket_signals.disconnected.connect(self.on_socket_disconnected)
        self.socket_signals.online_users_received.connect(self.handle_online_users)
        self.socket_signals.new_message_received.connect(self.handle_new_message)
        # --->

    def init_ui(self):
        # ... (Toàn bộ hàm init_ui() giữ nguyên, không thay đổi) ...
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', 'Inter', sans-serif;
                background-color: #ffffff;
            }
            
            /* ===== CỘT 1: SIDEBAR ===== */
            QFrame#sidebar {
                background-color: #f7f9fa;
                border-right: 1px solid #e0e0e0;
            }
            QFrame#sidebar_header {
                border-bottom: 1px solid #e0e0e0;
            }
            QLineEdit#search_bar {
                background-color: #e8eaed;
                border: none;
                border-radius: 18px;
                padding: 8px 16px;
                font-size: 14px;
                color: #111;
            }
            QLineEdit#search_bar:focus {
                background-color: #ffffff;
                border: 1px solid #0088cc;
            }
            
            QLabel#list_title {
                color: #555;
                font-size: 11px;
                font-weight: 600;
                text-transform: uppercase;
                padding: 12px 15px 4px 15px;
            }
            
            QListWidget {
                background-color: transparent;
                border: none;
                color: #111;
                outline: none;
                padding: 0px 8px;
            }
            QListWidget::item {
                padding: 14px;
                border: none;
                border-radius: 8px;
                background-color: transparent;
                margin: 2px 0;
            }
            QListWidget::item:hover { 
                background-color: #e7ebee;
            }
            QListWidget::item:selected { 
                background-color: #0088cc;
                color: white;
            }
            
            QListWidget#onlineList::item { color: #2f9e44; }
            QListWidget#onlineList::item:selected {
                background-color: #e6f7eb;
                color: #2b8a3e;
            }

            QFrame#user_footer {
                border-top: 1px solid #e0e0e0;
                padding: 10px;
            }
            QPushButton#profile_btn {
                background-color: #e7ebee;
                color: #333;
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-weight: 600;
                font-size: 13px;
                text-align: left;
                padding-left: 15px;
            }
            QPushButton#profile_btn:hover { background-color: #dfe3e7; }
            
            QLabel#placeholder {
                color: #777;
                font-size: 16px;
                background-color: #ffffff;
            }
        """)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ===== CỘT 1: SIDEBAR =====
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(320)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        sidebar_header = QFrame()
        sidebar_header.setObjectName("sidebar_header")
        sidebar_header.setFixedHeight(60)
        header_layout = QHBoxLayout(sidebar_header)
        header_layout.setContentsMargins(10, 10, 10, 10) 
        
        self.search_bar = QLineEdit(placeholderText="🔍 Tìm kiếm...")
        self.search_bar.setObjectName("search_bar")
        header_layout.addWidget(self.search_bar)
        sidebar_layout.addWidget(sidebar_header)

        chats_label = QLabel("Các đoạn chat")
        chats_label.setObjectName("list_title")
        sidebar_layout.addWidget(chats_label)
        self.chat_list = QListWidget()
        self.chat_list.setObjectName("chatList")
        sidebar_layout.addWidget(self.chat_list, 1) 
        self.chat_list.itemClicked.connect(self.on_chat_clicked)

        online_label = QLabel("Đang hoạt động")
        online_label.setObjectName("list_title")
        sidebar_layout.addWidget(online_label)
        self.online_list = QListWidget()
        self.online_list.setObjectName("onlineList")
        sidebar_layout.addWidget(self.online_list, 1) 
        self.online_list.itemClicked.connect(self.start_chat_with_user)
        
        user_footer = QFrame()
        user_footer.setObjectName("user_footer")
        user_footer_layout = QVBoxLayout(user_footer)
        user_footer_layout.setContentsMargins(10, 10, 10, 10)
        
        self.profile_btn = QPushButton("👤 Hồ sơ của tôi")
        self.profile_btn.setObjectName("profile_btn")
        self.profile_btn.setCursor(Qt.PointingHandCursor)
        user_footer_layout.addWidget(self.profile_btn)

        self.logout_btn = QPushButton("Đăng xuất")
        self.logout_btn.setCursor(Qt.PointingHandCursor)
        self.logout_btn.setStyleSheet("color: #c92a2a;")
        user_footer_layout.addWidget(self.logout_btn)
        
        sidebar_layout.addWidget(user_footer)
        main_layout.addWidget(sidebar)

        # ===== CỘT 2: KHUNG CHAT (STACKED LAYOUT) =====
        self.content_stack = QStackedLayout()
        
        self.placeholder = QLabel("Chọn một đoạn chat để bắt đầu\nhoặc tìm kiếm người dùng mới")
        self.placeholder.setObjectName("placeholder")
        self.placeholder.setAlignment(Qt.AlignCenter)
        
        self.chat_page = ChatPage(self)
        
        self.content_stack.addWidget(self.placeholder)
        self.content_stack.addWidget(self.chat_page)
        
        content_frame = QFrame()
        content_frame.setLayout(self.content_stack)
        main_layout.addWidget(content_frame, 1)

        # ===== CỘT 3: INFO PANEL (ẨN) =====
        self.info_panel = InfoPanel(self.parent) 
        self.info_panel.close_btn.clicked.connect(self.toggle_info_panel)
        self.info_panel.hide()
        main_layout.addWidget(self.info_panel)

        # Kết nối sự kiện
        self.search_bar.textChanged.connect(self.filter_lists)
        self.profile_btn.clicked.connect(self.show_profile)
        self.logout_btn.clicked.connect(self.logout)
        self.chat_page.info_button.clicked.connect(self.toggle_info_panel)


    # ==================================================
    #      CÁC HÀM XỬ LÝ (SLOTS) TRÊN GUI THREAD
    # ==================================================
    
    def on_socket_connected(self):
        self.socket_connected = True
        print("[Socket] Đã kết nối (GUI Thread)")

    def on_socket_disconnected(self):
        self.socket_connected = False
        print("[Socket] Đã ngắt kết nối (GUI Thread)")

    def handle_online_users(self, users):
        """Xử lý tín hiệu 'online_users_received'."""
        print("[Socket] Cập nhật online users (GUI Thread)")
        self.online_users = {uid: True for uid in users if uid != self.parent.user_id}
        self.update_online_list() # <--- An toàn để gọi

    def handle_new_message(self, msg):
        """Xử lý tín hiệu 'new_message_received'."""
        print("[Socket] Xử lý tin nhắn mới (GUI Thread)")
        chat_id = msg["chat_id"]
        sender = msg["sender_id"]
        
        if self.content_stack.currentWidget() == self.chat_page and self.current_chat_id == chat_id:
            try:
                key_dict = msg["aes_key_encrypted"]
                wrapped = key_dict.get(str(self.parent.user_id))
                if wrapped:
                    aes_key = crypto_client.unwrap_aes_key(wrapped, self.parent.private_key)
                    text = crypto_client.decrypt_aes_gcm(msg["content"], aes_key, msg["iv"], msg["tag"])
                else:
                    text = "[Không có khóa]"
            except Exception as e:
                text = f"[Lỗi giải mã: {e}]"
            
            self.chat_page.add_message(sender, text, sender == self.parent.user_id)
            
            token = self.parent.token
            threading.Thread(
                target=api_client.mark_chat_read, 
                args=(token, chat_id), 
                daemon=True
            ).start()
        else:
            print(f"[Tin nhắn mới] trong chat {chat_id}. Đang làm mới danh sách...")
            self.refresh_chats() # <--- An toàn để gọi

    # ==================================================
    #      LOGIC GIAO DIỆN (Giữ nguyên)
    # ==================================================

    def filter_lists(self):
        # ... (Giữ nguyên) ...
        search_text = self.search_bar.text().lower().strip()
        for i in range(self.chat_list.count()):
            item = self.chat_list.item(i)
            item_text = item.text().lower()
            item.setHidden(search_text not in item_text)
        for i in range(self.online_list.count()):
            item = self.online_list.item(i)
            item_text = item.text().lower()
            item.setHidden(search_text not in item_text)

    def show_profile(self):
        # ... (Giữ nguyên) ...
        profile_dialog = ProfilePage(self.parent)
        profile_dialog.exec_()

    def set_current_user_label(self):
        # ... (Giữ nguyên) ...
        if self.parent.user_id:
            status, data = api_client.get_user_info(self.parent.token, self.parent.user_id)
            if status == 200:
                name = data.get("full_name") or self.parent.user_id
                self.profile_btn.setText(f"👤 {name}")
            else:
                self.profile_btn.setText(f"👤 User {self.parent.user_id}")
        else:
            self.profile_btn.setText("Chưa đăng nhập")

    def toggle_info_panel(self):
        # ... (Giữ nguyên) ...
        if self.info_panel.isVisible():
            self.info_panel.hide()
        else:
            if self.current_other_user_id:
                self.info_panel.load_user_info(self.current_other_user_id)
                self.info_panel.show()

    def on_chat_clicked(self, item):
        # ... (Giữ nguyên) ...
        chat_id = item.data(Qt.UserRole)
        self.current_chat_id = chat_id
        self.info_panel.hide()
        self.current_other_user_id = None 
        
        token = self.parent.token
        if token and chat_id:
            threading.Thread(
                target=api_client.mark_chat_read, 
                args=(token, chat_id), 
                daemon=True
            ).start()
            
        font = item.font()
        font.setBold(False)
        item.setFont(font)
        original_text = item.text().split(" (")[0]
        item.setText(original_text)
        
        self.chat_page.load_chat(chat_id)
        self.content_stack.setCurrentWidget(self.chat_page)

    def start_chat_with_user(self, item):
        # ... (Giữ nguyên) ...
        uid = item.data(Qt.UserRole)
        if uid == self.parent.user_id:
            return
            
        status, chat = api_client.create_chat(
            self.parent.token, 
            name=f"Chat với User {uid}", 
            is_group=False, 
            members=[uid]
        )
        
        if status in (200, 201):
            chat_id = chat["chat_id"]
            self.current_chat_id = chat_id
            self.info_panel.hide()
            self.current_other_user_id = None 
            self.chat_page.load_chat(chat_id)
            self.content_stack.setCurrentWidget(self.chat_page)
            self.refresh_chats()
        else:
            print(f"Không thể tạo chat: {chat}")

    def logout(self):
        # ... (Giữ nguyên) ...
        try: 
            if self.socket_connected:
                sio.disconnect()
            self._socket_initialized = False 
            self.socket_connected = False
        except Exception as e: 
            print(f"[Socket] Lỗi disconnect: {e}")
        api_client.logout(self.parent.token)
        self.parent.token = None
        self.parent.user_id = None
        self.parent.private_key = None
        self.current_chat_id = None
        self.current_other_user_id = None
        self.chat_list.clear()
        self.online_list.clear()
        self.chat_page.clear_chat()
        self.info_panel.hide()
        self.content_stack.setCurrentWidget(self.placeholder)
        self.parent.layout.setCurrentWidget(self.parent.login_page)

    def update_online_list(self):
        # ... (Giữ nguyên) ...
        self.online_list.clear()
        for uid in self.online_users.keys():
            status, data = api_client.get_user_info(self.parent.token, uid)
            name = f"User {uid}" 
            if status == 200:
                name = data.get("full_name") or data.get("username")
            
            item = QListWidgetItem(f"🟢 {name}")
            item.setData(Qt.UserRole, uid)
            self.online_list.addItem(item)
            self.filter_lists()

    def refresh_chats(self):
        # ... (Gi-//- ...
        status, chats = api_client.get_chats(self.parent.token)
        self.chat_list.clear()
        if status == 200:
            chats_sorted = sorted(chats, key=lambda c: c.get('unread_count', 0), reverse=True)
            for c in chats_sorted:
                text = f"{c['name']}"
                unread_count = c.get('unread_count', 0)
                item = QListWidgetItem()
                item.setData(Qt.UserRole, c["chat_id"])
                
                font = item.font()
                if unread_count > 0:
                    text += f" ({unread_count})"
                    font.setBold(True)
                else:
                    font.setBold(False)
                
                item.setText(text)
                item.setFont(font)
                self.chat_list.addItem(item)
                
                if c["chat_id"] == self.current_chat_id:
                    self.chat_list.setCurrentItem(item)
            self.filter_lists()
        else:
            print(f"Lỗi khi refresh chats: {chats.get('msg')}")

    # ==================================================
    #      LOGIC SOCKET (SỬA ĐỂ EMIT TÍN HIỆU)
    # ==================================================
    
    def connect_socket(self):
        if self._socket_initialized: 
            try:
                if not self.socket_connected:
                    print("[Socket] Đang kết nối lại...")
                    sio.connect(SOCKET_URL, auth={"token": self.parent.token}, wait_timeout=5)
            except Exception as e:
                print(f"[Socket] Lỗi kết nối lại: {e}")
            return
            
        self._socket_initialized = True

        def _connect():
            try:
                print("[Socket] Đang kết nối lần đầu...")
                sio.connect(SOCKET_URL, auth={"token": self.parent.token}, wait_timeout=10)
            except Exception as e:
                print(f"[Socket] Lỗi kết nối: {e}")

        threading.Thread(target=_connect, daemon=True).start()

        # <--- SỬA ĐỔI: TẤT CẢ CÁC HÀM NÀY CHỈ EMIT TÍN HIỆU
        @sio.on("connect")
        def on_connect():
            self.socket_signals.connected.emit()

        @sio.on("disconnect")
        def on_disconnect():
            self.socket_signals.disconnected.emit()

        @sio.on("online_users")
        def on_online(users):
            self.socket_signals.online_users_received.emit(users)

        @sio.on("receive_message")
        def on_receive(msg):
            self.socket_signals.new_message_received.emit(msg)
        # --->