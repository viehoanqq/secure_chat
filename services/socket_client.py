import socketio

sio = socketio.Client()
username = None

@sio.on("connect")
def on_connect():
    print("✅ Connected to server")
    sio.emit("join", {"username": username})

@sio.on("disconnect")
def on_disconnect():
    print("❌ Disconnected from server")

@sio.on("receive_message")
def on_receive(data):
    sender = data["sender"]
    message = data["message"]
    if sender != username:
        print(f"\n💬 {sender}: {message}")
        print("You: ", end="", flush=True)

@sio.on("system_message")
def on_system(data):
    print(f"\n[System] {data['msg']}")
    print("You: ", end="", flush=True)

if __name__ == "__main__":
    username = input("Enter your username: ").strip()
    sio.connect("http://127.0.0.1:5001", transports=["websocket"])

    print("You can now chat! Type messages below.")
    while True:
        try:
            to = input("Send to: ").strip()
            msg = input("You: ").strip()
            sio.emit("send_message", {"sender": username, "receiver": to, "message": msg})
        except KeyboardInterrupt:
            print("\nExiting...")
            break
