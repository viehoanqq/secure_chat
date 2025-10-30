# chat_gui.py
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading, base64
import socketio
import traceback

# Import your existing service modules
from services import api_client
from services import crypto_client

SIO_SERVER = "http://127.0.0.1:5001"   # socket server
REST_BASE = "http://127.0.0.1:5000"    # rest api (api_client already uses this)

sio = socketio.Client()

class SecureChatGUI:
    def __init__(self, root):
        self.root = root
        root.title("Secure Chat - GUI (Encrypted, Realtime)")
        self.token = None
        self.user_id = None
        self.username = None
        self.private_key_pem = None  # user's private key (PEM str)

        # Top: Login / Private key
        top = ttk.Frame(root)
        top.pack(fill="x", padx=8, pady=6)

        ttk.Label(top, text="Username:").grid(row=0, column=0, sticky="e")
        self.entry_username = ttk.Entry(top, width=20)
        self.entry_username.grid(row=0, column=1, padx=4)

        ttk.Label(top, text="Password:").grid(row=0, column=2, sticky="e")
        self.entry_password = ttk.Entry(top, width=20, show="*")
        self.entry_password.grid(row=0, column=3, padx=4)

        self.btn_login = ttk.Button(top, text="Login", command=self.login)
        self.btn_login.grid(row=0, column=4, padx=6)

        ttk.Label(top, text="Private Key PEM:").grid(row=1, column=0, sticky="ne", pady=6)
        self.txt_priv = scrolledtext.ScrolledText(top, width=60, height=6)
        self.txt_priv.grid(row=1, column=1, columnspan=4, sticky="w")
        self.btn_load_priv = ttk.Button(top, text="Load file", command=self.load_private_file)
        self.btn_load_priv.grid(row=1, column=5, padx=4)

        # Middle: Receiver selection / or paste public key
        mid = ttk.Frame(root)
        mid.pack(fill="x", padx=8, pady=6)
        ttk.Label(mid, text="Receiver user_id (or leave empty and paste public key):").grid(row=0, column=0, sticky="w")
        self.entry_receiver_id = ttk.Entry(mid, width=12)
        self.entry_receiver_id.grid(row=0, column=1, padx=4)
        ttk.Label(mid, text="OR Receiver public key (PEM):").grid(row=1, column=0, sticky="nw")
        self.txt_receiver_pub = scrolledtext.ScrolledText(mid, width=60, height=6)
        self.txt_receiver_pub.grid(row=1, column=1, columnspan=4)

        # Chat area
        chat_frame = ttk.Frame(root)
        chat_frame.pack(fill="both", expand=True, padx=8, pady=6)

        self.messages_box = scrolledtext.ScrolledText(chat_frame, width=80, height=20, state="disabled")
        self.messages_box.pack(side="top", fill="both", expand=True)

        bottom = ttk.Frame(root)
        bottom.pack(fill="x", padx=8, pady=6)
        self.entry_message = ttk.Entry(bottom, width=70)
        self.entry_message.pack(side="left", padx=4)
        self.btn_send = ttk.Button(bottom, text="Send", command=self.on_send_clicked)
        self.btn_send.pack(side="left", padx=4)

        # socket handlers
        sio.on("connect", self.on_connect)
        sio.on("disconnect", self.on_disconnect)
        sio.on("receive_message", self.on_receive_message)

        self.append_message("Info: Ready. Please login and paste your private key PEM.")

    def load_private_file(self):
        path = filedialog.askopenfilename(filetypes=[("PEM files", "*.pem;*.key;*.txt"), ("All files","*.*")])
        if path:
            with open(path, "r", encoding="utf-8") as f:
                data = f.read()
            self.txt_priv.delete("1.0", tk.END)
            self.txt_priv.insert(tk.END, data)

    def append_message(self, text):
        self.messages_box.config(state="normal")
        self.messages_box.insert(tk.END, text + "\n")
        self.messages_box.see(tk.END)
        self.messages_box.config(state="disabled")

    def login(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()
        priv = self.txt_priv.get("1.0", tk.END).strip()
        if not username or not password:
            messagebox.showerror("Error", "Username and password required")
            return
        if not priv:
            messagebox.showerror("Error", "Private key PEM required")
            return

        status = None
        try:
            token, user_id, data = api_client.login(username, password)
            if not token:
                messagebox.showerror("Login failed", f"{data.get('msg', 'no message')}")
                return
            self.token = token
            self.user_id = user_id
            self.username = username
            self.private_key_pem = priv
            self.append_message(f"Logged in as {username} (id={user_id})")
        except Exception as e:
            messagebox.showerror("Error", f"Login exception: {e}")
            return

        # connect socket after login
        try:
            if not sio.connected:
                sio.connect(SIO_SERVER, transports=["websocket"])
        except Exception as e:
            self.append_message(f"Socket connect error: {e}")
            traceback.print_exc()

    # socket callbacks
    def on_connect(self, *args):
        self.append_message("Socket: connected")
        # join room by username so server can route by username
        if self.username:
            sio.emit("join", {"username": self.username})

    def on_disconnect(self, *args):
        self.append_message("Socket: disconnected")

    def on_receive_message(self, data):
        # data: {"sender": sender, "payload": {...}}
        try:
            sender = data.get("sender")
            payload = data.get("payload", {})
            ciphertext = payload.get("ciphertext")
            iv = payload.get("iv")
            tag = payload.get("tag")
            aes_key_encrypted = payload.get("aes_key_encrypted")

            # unwrap AES key using our private key
            if not self.private_key_pem:
                self.append_message(f"[{sender}] <encrypted message received; private key not provided>")
                return
            try:
                aes_key = crypto_client.unwrap_aes_key(aes_key_encrypted, self.private_key_pem)
            except Exception as ex:
                self.append_message(f"[{sender}] Failed to unwrap AES key: {ex}")
                return

            # decrypt payload
            try:
                plaintext = crypto_client.decrypt_aes_gcm(
                    ciphertext_b64=ciphertext,
                    iv_b64=iv,
                    tag_b64=tag,
                    key=aes_key
                )
            except Exception as ex:
                self.append_message(f"[{sender}] Failed to decrypt: {ex}")
                return

            self.append_message(f"{sender}: {plaintext}")
        except Exception as e:
            self.append_message(f"Receive handler error: {e}")
            traceback.print_exc()

    def on_send_clicked(self):
        text = self.entry_message.get().strip()
        if not text:
            return
        if not self.token or not self.user_id:
            messagebox.showerror("Not logged in", "Please login first")
            return

        # determine receiver public key
        receiver_id_str = self.entry_receiver_id.get().strip()
        receiver_pub_pem = self.txt_receiver_pub.get("1.0", tk.END).strip()
        receiver_id = None
        receiver_username = None
        if receiver_id_str:
            try:
                receiver_id = int(receiver_id_str)
            except:
                messagebox.showerror("Receiver id", "Receiver id must be integer or leave empty to paste public key")
                return
            # get user info from REST to obtain public_key and username
            status, data = api_client.get_user_info(self.token, receiver_id)
            if status != 200:
                messagebox.showerror("Error", f"Get user info failed: {data.get('msg')}")
                return
            receiver_pub_pem = data.get("public_key")
            receiver_username = data.get("username")
        else:
            if not receiver_pub_pem:
                messagebox.showerror("Receiver", "Provide receiver id or paste receiver public key PEM")
                return
            # No receiver username known; we will ask user to type receiver username in a small prompt
            receiver_username = simple_input_dialog("Enter receiver username (room name):")
            if not receiver_username:
                messagebox.showerror("Receiver", "Receiver username required when using public key paste")
                return

        # create AES key and encrypt
        try:
            aes_key = crypto_client.generate_aes_key()
            enc = crypto_client.encrypt_aes_gcm(text, aes_key)
            wrapped = crypto_client.wrap_aes_key(aes_key, receiver_pub_pem)
        except Exception as e:
            messagebox.showerror("Crypto error", f"Encryption failed: {e}")
            return

        payload = {
            "ciphertext": enc["ciphertext"],
            "iv": enc["iv"],
            "tag": enc["tag"],
            "aes_key_encrypted": wrapped
        }

        # 1) Persist to REST (if we have receiver_id)
        if receiver_id:
            status, resp = api_client.send_message(self.token, receiver_id, enc["ciphertext"], wrapped, enc["iv"], enc["tag"])
            if status not in (200, 201):
                self.append_message(f"Warning: REST send failed: {resp.get('msg')}")
        else:
            # no persistence if user only pasted public key (optional)
            pass

        # 2) Emit via socket for realtime
        try:
            sio.emit("send_message", {
                "sender": self.username,
                "receiver": receiver_username,
                "payload": payload
            })
        except Exception as e:
            self.append_message(f"Socket emit error: {e}")
            traceback.print_exc()

        # show message locally
        self.append_message(f"{self.username} (you): {text}")
        self.entry_message.delete(0, tk.END)

def simple_input_dialog(prompt):
    dlg = tk.Toplevel()
    dlg.title("Input")
    lbl = ttk.Label(dlg, text=prompt)
    lbl.pack(padx=8, pady=8)
    ent = ttk.Entry(dlg, width=40)
    ent.pack(padx=8, pady=8)
    res = {"value": None}
    def ok():
        res["value"] = ent.get().strip()
        dlg.destroy()
    def cancel():
        dlg.destroy()
    btnf = ttk.Frame(dlg)
    btnf.pack(pady=6)
    ttk.Button(btnf, text="OK", command=ok).pack(side="left", padx=6)
    ttk.Button(btnf, text="Cancel", command=cancel).pack(side="left", padx=6)
    dlg.grab_set()
    dlg.wait_window()
    return res["value"]

def run_gui():
    root = tk.Tk()
    app = SecureChatGUI(root)
    root.mainloop()

if __name__ == "__main__":
    # run in main thread
    gui_thread = threading.Thread(target=run_gui)
    gui_thread.start()
