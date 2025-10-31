# chat_gui.py
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import socketio
from services import api_client, crypto_client

SIO_SERVER = "http://127.0.0.1:5001"
sio = socketio.Client()

class SecureChatGUI:
    def __init__(self, root):
        self.root = root
        root.title("Secure Chat - Auto Key + Register")
        root.geometry("1000x700")

        self.token = None
        self.user_id = None
        self.username = None
        self.private_key_pem = None

        self.user_map = {}
        self.reverse_map = {}

        self.build_ui()

        sio.on("connect", self.on_connect)
        sio.on("disconnect", self.on_disconnect)
        sio.on("receive_message", self.on_receive_message)

        self.append_message("Ready. Use Login or Register.")

    def build_ui(self):
        # === Login & Register ===
        auth_frame = ttk.LabelFrame(self.root, text=" Authentication ")
        auth_frame.pack(fill="x", padx=12, pady=10)

        # Row 1: Username
        ttk.Label(auth_frame, text="Username:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.entry_username = ttk.Entry(auth_frame, width=25)
        self.entry_username.grid(row=0, column=1, padx=5, pady=5)

        # Row 2: Password
        ttk.Label(auth_frame, text="Password:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.entry_password = ttk.Entry(auth_frame, width=25, show="*")
        self.entry_password.grid(row=1, column=1, padx=5, pady=5)

        # Buttons
        btn_frame = ttk.Frame(auth_frame)
        btn_frame.grid(row=0, column=2, rowspan=2, padx=15, pady=5)

        self.btn_login = ttk.Button(btn_frame, text="Login", command=self.login)
        self.btn_login.pack(pady=3, fill="x")

        self.btn_register = ttk.Button(btn_frame, text="Register", command=self.register)
        self.btn_register.pack(pady=3, fill="x")

        # === Key Display (khi register) ===
        key_frame = ttk.LabelFrame(self.root, text=" Generated Keys (Check & Copy) ")
        key_frame.pack(fill="both", expand=False, padx=12, pady=8)

        self.key_display = scrolledtext.ScrolledText(key_frame, height=10, font=("Courier", 9))
        self.key_display.pack(fill="both", expand=True, padx=8, pady=8)
        self.key_display.insert(tk.END, "Keys will appear here after registration...\n")
        self.key_display.config(state="disabled")

        # === Chat Controls ===
        chat_ctrl = ttk.Frame(self.root)
        chat_ctrl.pack(fill="x", padx=12, pady=8)

        ttk.Label(chat_ctrl, text="Chat with User ID:").pack(side="left")
        self.entry_receiver_id = ttk.Entry(chat_ctrl, width=15)
        self.entry_receiver_id.pack(side="left", padx=5)
        self.btn_load_chat = ttk.Button(chat_ctrl, text="Load Chat", command=self.load_chat)
        self.btn_load_chat.pack(side="left", padx=5)

        # === Messages ===
        msg_frame = ttk.LabelFrame(self.root, text=" Messages ")
        msg_frame.pack(fill="both", expand=True, padx=12, pady=8)

        self.messages_box = scrolledtext.ScrolledText(msg_frame, state="disabled", height=18)
        self.messages_box.pack(fill="both", expand=True, padx=8, pady=8)

        # === Input ===
        input_frame = ttk.Frame(self.root)
        input_frame.pack(fill="x", padx=12, pady=8)

        self.entry_message = ttk.Entry(input_frame, width=80)
        self.entry_message.pack(side="left", fill="x", expand=True, padx=5)
        self.entry_message.bind("<Return>", lambda e: self.send_message())

        self.btn_send = ttk.Button(input_frame, text="Send", command=self.send_message)
        self.btn_send.pack(side="left", padx=5)

    def append_message(self, text):
        self.messages_box.config(state="normal")
        self.messages_box.insert(tk.END, text + "\n")
        self.messages_box.see(tk.END)
        self.messages_box.config(state="disabled")

    def append_key(self, text):
        self.key_display.config(state="normal")
        self.key_display.insert(tk.END, text + "\n")
        self.key_display.see(tk.END)
        self.key_display.config(state="disabled")

    def clear_keys(self):
        self.key_display.config(state="normal")
        self.key_display.delete("1.0", tk.END)
        self.key_display.insert(tk.END, "Keys will appear here after registration...\n")
        self.key_display.config(state="disabled")

    def register(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Username and password required")
            return

        if len(password) < 4:
            messagebox.showerror("Error", "Password too short (min 4 chars)")
            return

        try:
            self.clear_keys()
            self.append_message(f"Generating key pair for '{username}'...")

            # 1. Sinh key
            private_pem, public_pem = crypto_client.generate_rsa_keypair()
            self.append_key("PRIVATE KEY (DO NOT SHARE!):")
            self.append_key(private_pem)
            self.append_key("\n" + "="*60)
            self.append_key("PUBLIC KEY (Will be sent to server):")
            self.append_key(public_pem)
            self.append_key("\n" + "="*60)
            self.append_key("Key pair generated successfully!")

            self.append_message("Registering user on server...")
            status, data = api_client.register(username, password, public_pem)

            if status == 400 and "already exists" in data.get("msg", ""):
                messagebox.showerror("Error", f"User '{username}' already exists. Use Login.")
                return
            elif status != 201:
                raise Exception(data.get("msg", "Unknown error"))

            self.append_message("User registered! Saving private key securely...")

            # 2. Lưu private key (mã hóa bằng password)
            crypto_client.save_private_key(username, private_pem, password)
            self.append_message("Private key encrypted and saved locally.")

            # 3. Tự động login
            if messagebox.askyesno("Success", "Register successful!\nLogin now?"):
                self.login()
            else:
                self.append_message("You can now login with this username + password.")

        except Exception as e:
            messagebox.showerror("Register Failed", str(e))
            self.append_message(f"Register error: {e}")

    def login(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Username and password required")
            return

        # Thử login
        token, user_id, data = api_client.login(username, password)
        private_pem = None

        if not token:
            messagebox.showerror("Login Failed", "Invalid username or password")
            return

        # Load private key
        try:
            private_pem = crypto_client.load_private_key(username, password)
            self.append_message("Private key loaded from encrypted storage")
        except Exception as e:
            messagebox.showerror("Key Error", f"Cannot decrypt private key:\n{e}\nWrong password?")
            return

        # Success
        self.token = token
        self.user_id = user_id
        self.username = username
        self.private_key_pem = private_pem

        self.user_map[username] = user_id
        self.reverse_map[user_id] = username

        self.append_message(f"Logged in as {username} (ID: {user_id})")

        # Connect socket
        if not sio.connected:
            try:
                sio.connect(SIO_SERVER, transports=["websocket"])
            except Exception as e:
                self.append_message(f"Socket error: {e}")

    def on_connect(self):
        self.append_message("Realtime server connected")
        sio.emit("join", {"username": self.username})

    def on_disconnect(self):
        self.append_message("Realtime server disconnected")

    def load_chat(self):
        try:
            receiver_id = int(self.entry_receiver_id.get().strip())
        except:
            messagebox.showerror("Error", "Invalid User ID")
            return

        status, data = api_client.get_user_info(self.token, receiver_id)
        if status != 200:
            messagebox.showerror("Error", data.get("msg"))
            return

        username = data["username"]
        self.user_map[username] = receiver_id
        self.reverse_map[receiver_id] = username

        self.append_message(f"--- Chatting with {username} (ID: {receiver_id}) ---")
        threading.Thread(target=self.fetch_history, args=(receiver_id,), daemon=True).start()

    def fetch_history(self, user_id):
        status, data = api_client.get_messages(self.token, user_id)
        if status != 200:
            self.append_message(f"History load failed: {data.get('msg')}")
            return
        for msg in data:
            sender = self.reverse_map.get(msg["sender_id"], f"User{msg['sender_id']}")
            try:
                aes_key = crypto_client.unwrap_aes_key(msg["aes_key_encrypted"], self.private_key_pem)
                text = crypto_client.decrypt_aes_gcm(msg["content"], msg["iv"], msg["tag"], aes_key)
                self.append_message(f"{sender}: {text}")
            except:
                self.append_message(f"{sender}: [decrypt failed]")

    def send_message(self):
        text = self.entry_message.get().strip()
        if not text or not self.token:
            return

        try:
            receiver_id = int(self.entry_receiver_id.get().strip())
        except:
            messagebox.showerror("Error", "Enter valid receiver ID")
            return

        # LẤY PUBLIC KEY CỦA NGƯỜI NHẬN
        status, data = api_client.get_user_info(self.token, receiver_id)
        if status != 200:
            messagebox.showerror("Error", "User not found")
            return  

        receiver_pub = data["public_key"]
        receiver_name = data["username"]

        # MÃ HÓA TIN NHẮN
        aes_key = crypto_client.generate_aes_key()
        enc = crypto_client.encrypt_aes_gcm(text, aes_key)

        # Wrap AES key cho receiver và sender
        wrapped_for_receiver = crypto_client.wrap_aes_key(aes_key, receiver_pub)
        wrapped_for_sender = crypto_client.wrap_aes_key(aes_key, self.private_key_pem)  # Dùng chính mình

        payload = {
            "ciphertext": enc["ciphertext"],
            "iv": enc["iv"],
            "tag": enc["tag"],
            "aes_key_encrypted": wrapped_for_receiver,
            "aes_key_encrypted_sender": wrapped_for_sender  # thêm key cho chính mình
        }

        # GỬI REST
        api_client.send_message(self.token, receiver_id, enc["ciphertext"], wrapped_for_receiver, enc["iv"], enc["tag"])

        # GỬI REALTIME
        sio.emit("send_message", {
            "sender": self.username,
            "sender_id": self.user_id,
            "receiver": receiver_name,
            "payload": payload
        })

        self.append_message(f"You: {text}")
        self.entry_message.delete(0, tk.END)

    def on_receive_message(self, data):
        sender = data.get("sender")
        sender_id = data.get("sender_id")
        payload = data.get("payload", {})

        if sender and sender_id:
            self.user_map[sender] = sender_id
            self.reverse_map[sender_id] = sender

        try:
            # Nếu là tin nhắn của chính mình, dùng wrapped_for_sender
            if sender_id == self.user_id and "aes_key_encrypted_sender" in payload:
                aes_key = crypto_client.unwrap_aes_key(payload["aes_key_encrypted_sender"], self.private_key_pem)
            else:
                aes_key = crypto_client.unwrap_aes_key(payload["aes_key_encrypted"], self.private_key_pem)

            text = crypto_client.decrypt_aes_gcm(
                payload["ciphertext"], payload["iv"], payload["tag"], aes_key
            )
            self.append_message(f"{sender}: {text}")
        except Exception as e:
            self.append_message(f"{sender}: [decrypt failed]")

def run_gui():
    root = tk.Tk()
    app = SecureChatGUI(root)
    root.mainloop()

if __name__ == "__main__":
    run_gui()