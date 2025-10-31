# socket_server.py
from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import logging

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# username -> sid
connected_users = {}

@socketio.on("connect")
def handle_connect():
    sid = request.sid
    app.logger.info(f"Client connected: sid={sid}")

@socketio.on("disconnect")
def handle_disconnect():
    sid = request.sid
    removed = []
    for username, u_sid in list(connected_users.items()):
        if u_sid == sid:
            removed.append(username)
            connected_users.pop(username, None)
            try:
                leave_room(username)
            except:
                pass
    app.logger.info(f"Client disconnected: sid={sid}, removed={removed}")

@socketio.on("join")
def handle_join(data):
    username = data.get("username")
    if not username:
        emit("system_message", {"msg": "join failed: missing username"}, room=request.sid)
        return
    username = str(username).strip()
    if not username:
        return
    join_room(username)
    connected_users[username] = request.sid
    app.logger.info(f"[JOIN] username={username} sid={request.sid}")
    emit("system_message", {"msg": f"{username} joined"}, room=username)

@socketio.on("send_message")
def handle_send_message(data):
    sender = data.get("sender")
    receiver = data.get("receiver")
    sender_id = data.get("sender_id")  # THÊM
    payload = data.get("payload")

    if not all([sender, receiver, sender_id, isinstance(payload, dict)]):
        emit("error", {"msg": "Invalid message format"}, room=request.sid)
        return

    app.logger.info(f"[MESSAGE] {sender}({sender_id}) -> {receiver}")

    message_event = {
        "sender": sender,
        "sender_id": sender_id,
        "payload": payload
    }

    # Gửi cho người nhận
    emit("receive_message", message_event, room=receiver)
    # Gửi lại cho người gửi (hiển thị local)
    emit("receive_message", message_event, room=sender)

@app.route("/_connected_users")
def list_connected():
    return {"connected_users": list(connected_users.keys())}

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.logger.info("Starting Socket.IO server on http://0.0.0.0:5001")
    socketio.run(app, host="0.0.0.0", port=5001)