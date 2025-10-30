from flask import Flask
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# Ghi nhớ ai đã join (để debug)
connected_users = {}

@socketio.on("connect")
def handle_connect():
    print("Client connected")

@socketio.on("disconnect")
def handle_disconnect():
    print("Client disconnected")

@socketio.on("join")
def handle_join(data):
    username = data.get("username")
    if not username:
        return
    join_room(username)
    connected_users[username] = request.sid
    print(f"[JOIN] {username} joined room '{username}'")
    emit("system_message", {"msg": f"{username} joined the chat."}, broadcast=True)

@socketio.on("send_message")
def handle_send_message(data):
    sender = data.get("sender")
    receiver = data.get("receiver")
    message = data.get("message")

    print(f"[MESSAGE] {sender} -> {receiver}: {message}")
    # Gửi riêng cho người nhận
    emit("receive_message", {"sender": sender, "message": message}, room=receiver)
    # Gửi phản hồi lại cho người gửi (hiển thị tin của mình)
    emit("receive_message", {"sender": sender, "message": message}, room=sender)

if __name__ == "__main__":
    print("Server running at http://127.0.0.1:5001")
    socketio.run(app, host="0.0.0.0", port=5001)
