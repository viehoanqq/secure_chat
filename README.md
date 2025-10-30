# Secure Chat  
End-to-End Encrypted Real-Time Messaging — Secure Chat là ứng dụng trò chuyện thời gian thực với mã hóa đầu cuối (E2EE). Ứng dụng dùng Flask + SQLAlchemy cho backend, WebSocket cho realtime, và kết hợp RSA + AES‑GCM để bảo vệ nội dung. Mọi tin nhắn lưu trữ ở trạng thái đã mã hóa.

---

## Mục lục

- [Tính năng chính](#tính-năng-chính)  
- [Cấu trúc dự án](#cấu-trúc-dự-án)  
- [Yêu cầu & cài đặt nhanh](#yêu-cầu--cài-đặt-nhanh)  
- [Cấu hình](#cấu-hình)  
- [Chạy ứng dụng](#chạy-ứng-dụng)  
- [API chính](#api-chính)  
- [Ghi chú bảo mật](#ghi-chú-bảo-mật)

---

## Tính năng chính

- Đăng ký / Đăng nhập (JWT)
- Trao đổi khóa công khai qua API
- Mã hóa: RSA (trao đổi khóa) + AES‑GCM (nội dung)
- Chat thời gian thực qua WebSocket (Flask-SocketIO)
- Lưu trữ tin nhắn ở dạng đã mã hóa
- Tự triển khai thuật toán mật mã (không dùng thư viện Crypto có sẵn)

---

## Cấu trúc dự án

```
secure_chat/
├── app.py
├── config.py
├── models/
│   ├── user.py
│   └── message.py
├── routes/
│   ├── auth_routes.py
│   └── chat_routes.py
├── services/
│   ├── api_client.py
│   ├── crypto_client.py
│   └── socket_client.py
├── socket_server.py
├── requirements.txt
└── test.py
```

---

## Yêu cầu & cài đặt nhanh

Yêu cầu: Python 3.11+

1. Tạo venv và kích hoạt
    - Windows:
      ```
      python -m venv venv
      venv\Scripts\activate
      ```
    - macOS / Linux:
      ```
      python -m venv venv
      source venv/bin/activate
      ```
2. Cài đặt phụ thuộc
    ```
    pip install -r requirements.txt
    ```

---

## Cấu hình

Mở `config.py` và chỉnh `SQLALCHEMY_DATABASE_URI`. Ví dụ:

- MySQL:
  ```
  SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:@localhost/secure_chat"
  ```
  ```
  SQLALCHEMY_DATABASE_URI = "sqlite:///secure_chat.db"
  ```

Khởi tạo DB:
```
Import database có sẵn trong /database vào MySQL bằng phpMyAdmin hoặc dòng lệnh

---

## Chạy ứng dụng

- Chạy API server:
  ```
  python app.py
  ```
- Mặc định: http://127.0.0.1:5000

---

## API chính

- POST /auth/register — Đăng ký
- POST /auth/login — Đăng nhập và nhận JWT
- GET /auth/user/<id> — Lấy public key của user
- POST /chat/send — Gửi tin nhắn (payload đã mã hóa)
- GET /chat/messages/<id> — Lấy tin nhắn (đã mã hóa) với user id

---

## Ghi chú bảo mật

- Mã hóa thực hiện bằng kết hợp RSA (để trao đổi khóa) và AES‑GCM (để mã hóa nội dung).  
- Tất cả thao tác mật mã được triển khai nội bộ theo yêu cầu dự án; kiểm thử và audit kỹ lưỡng trước khi sử dụng trong môi trường sản xuất.  
- Không lưu trữ private key trên server; private key phải nằm trên client hoặc môi trường an toàn của người dùng.

---

Nếu bạn muốn, tôi có thể:
- Thêm hướng dẫn cấu hình Docker / docker-compose
- Viết ví dụ request cURL hoặc Postman collection
- Thêm README badge cho CI / coverage
