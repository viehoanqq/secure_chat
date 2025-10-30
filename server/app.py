# socket_server.py
from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import logging

# Basic Flask + SocketIO setup
app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
# Use threading mode to avoid requiring eventlet/gevent on Windows
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# Mapping username -> sid
connected_users = {}

# -------- Handlers --------
@socketio.on("connect")
def handle_connect():
    sid = request.sid
    app.logger.info(f"Client connected: sid={sid}")
    # do not auto-assign username here; wait for 'join' event

@socketio.on("disconnect")
def handle_disconnect():
    sid = request.sid
    # remove any username that has this sid
    removed = []
    for username, u_sid in list(connected_users.items()):
        if u_sid == sid:
            removed.append(username)
            connected_users.pop(username, None)
            try:
                leave_room(username)
            except Exception:
                pass
    app.logger.info(f"Client disconnected: sid={sid}, removed users={removed}")

@socketio.on("join")
def handle_join(data):
    """
    Client should emit:
      sio.emit('join', {'username': 'hoang'})
    """
    username = (data.get("username") if isinstance(data, dict) else None)
    if not username:
        emit("system_message", {"msg": "join failed: missing username"}, room=request.sid)
        return

    username = str(username).strip()
    if not username:
        emit("system_message", {"msg": "join failed: empty username"}, room=request.sid)
        return

    # join room and register sid
    join_room(username)
    connected_users[username] = request.sid
    app.logger.info(f"[JOIN] username={username} sid={request.sid}")
    emit("system_message", {"msg": f"{username} joined"}, room=username)

@socketio.on("send_message")
def handle_send_message(data):
    """
    Expected data:
    {
      "sender": "hoang",
      "receiver": "alice",
      "payload": {
         "ciphertext": "...",    # base64
         "iv": "...",            # base64
         "tag": "...",           # base64
         "aes_key_encrypted": "..."  # base64 (RSA-encrypted)
      }
    }
    Server will forward the payload as-is to receiver and to sender (for local display).
    """
    if not isinstance(data, dict):
        app.logger.warning("send_message: invalid data (not dict)")
        return

    sender = data.get("sender")
    receiver = data.get("receiver")
    payload = data.get("payload")

    # basic validation
    if not sender or not receiver or not isinstance(payload, dict):
        app.logger.warning("send_message: missing fields: sender/receiver/payload")
        emit("error", {"msg": "send_message failed: missing sender/receiver/payload"}, room=request.sid)
        return

    app.logger.info(f"[MESSAGE] {sender} -> {receiver}: (encrypted payload)")

    message_event = {
        "sender": sender,
        "payload": payload
    }

    # forward to receiver room (if anyone joined that room)
    try:
        emit("receive_message", message_event, room=receiver)
    except Exception as e:
        app.logger.exception(f"Error emitting to receiver {receiver}: {e}")

    # also forward to sender room so sender can render its own message
    try:
        emit("receive_message", message_event, room=sender)
    except Exception as e:
        app.logger.exception(f"Error emitting back to sender {sender}: {e}")

# Optional: endpoint to list connected users (for debug)
@app.route("/_connected_users")
def list_connected():
    return {"connected_users": connected_users}

if __name__ == "__main__":
    # enable logging to console
    logging.basicConfig(level=logging.INFO)
    app.logger.info("Starting Socket.IO server on http://0.0.0.0:5001")
    socketio.run(app, host="0.0.0.0", port=5001)
