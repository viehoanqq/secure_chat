# Secure Chat  
**End-to-End Encrypted Real-Time Messaging**

Secure Chat là ứng dụng nhắn tin **bảo mật đầu cuối (E2EE)**, sử dụng **WebSocket** để giao tiếp thời gian thực và **Flask + SQLAlchemy** để quản lý dữ liệu.  
Mọi tin nhắn được mã hóa bằng **RSA + AES-GCM**, đảm bảo **chỉ người nhận mới có thể giải mã**.

---

## 1. Giới thiệu

Ứng dụng cho phép **hai người dùng trò chuyện trực tiếp, an toàn tuyệt đối**.  
Tính năng nổi bật:

- Đăng ký / Đăng nhập với **JWT**
- Trao đổi khóa công khai qua API
- Mã hóa tin nhắn bằng **RSA (trao đổi khóa)** + **AES-GCM (nội dung)**
- Chat **thời gian thực** qua **WebSocket**
- Lưu trữ tin nhắn đã mã hóa trong CSDL

> **Không dùng thư viện `Crypto` có sẵn** — toàn bộ thuật toán được **tự viết bằng toán học thuần**.

---

## 2. Cấu trúc thư mục

```bash
secure_chat/
├── app.py                     # Ứng dụng Flask chính
├── config.py                  # Cấu hình DB, JWT, Secret Key
│
├── models/
│   ├── user.py                # Model User (username, password_hash, public_key, ...)
│   └── message.py             # Model Message (sender_id, receiver_id, encrypted_data, iv, tag)
│
├── routes/
│   ├── auth_routes.py         # /auth/register, /auth/login
│   └── chat_routes.py         # /chat/send, /chat/messages/<id>
│
├── services/
│   ├── api_client.py          # Gọi REST API (đăng nhập, gửi tin, lấy key)
│   ├── crypto_client.py       # RSA, AES-GCM, OAEP, PBKDF2 (toàn bộ tự code toán học)
│   └── socket_client.py       # Client WebSocket (chat thời gian thực)
│
├── socket_server.py           # WebSocket Server (Flask-SocketIO)
│
├── requirements.txt           # Các thư viện cần thiết
└── test.py                    # Kiểm thử toàn bộ luồng E2EE
