# test.py
from services.api_client import register, login, get_user_info, send_message, get_messages
from services.crypto_client import generate_rsa_keypair, generate_aes_key, encrypt_aes_gcm, decrypt_aes_gcm, wrap_aes_key, unwrap_aes_key
import sys

def main():
    print("=== Secure Chat Test ===")
    
    # 1. Nhập username/password
    sender_username = input("Enter sender username: ")
    sender_password = input("Enter sender password: ")
    receiver_username = input("Enter receiver username: ")
    receiver_password = input("Enter receiver password: ")
    
    # 2. Tạo keypair cho sender/receiver
    sender_priv, sender_pub = generate_rsa_keypair()
    receiver_priv, receiver_pub = generate_rsa_keypair()
    
    # 3. Register user
    register(sender_username, sender_password, sender_pub)
    register(receiver_username, receiver_password, receiver_pub)
    
    # 4. Login
    sender_token, sender_id, _ = login(sender_username, sender_password)
    if not sender_token:
        print("Sender login failed")
        sys.exit(1)
    receiver_token, receiver_id, _ = login(receiver_username, receiver_password)
    if not receiver_token:
        print("Receiver login failed")
        sys.exit(1)
    
    print(f"[DEBUG] Sender token: {sender_token}, user_id={sender_id}")
    print(f"[DEBUG] Receiver token: {receiver_token}, user_id={receiver_id}")
    
    # 5. Lấy public key receiver
    status, data = get_user_info(sender_token, receiver_id)
    if status != 200:
        print("Failed to get receiver's public key. Exiting.")
        sys.exit(1)
    receiver_pub_key = data["public_key"]
    
    # 6. Tạo AES key và mã hóa AES key bằng RSA receiver
    aes_key = generate_aes_key()
    wrapped_aes = wrap_aes_key(aes_key, receiver_pub_key)
    
    # 7. Nhập message và mã hóa bằng AES
    plaintext = input("Enter message to send: ")
    enc = encrypt_aes_gcm(plaintext, aes_key)
    
    # 8. Gửi message
    send_message(sender_token, receiver_id, enc["ciphertext"], wrapped_aes, enc["iv"], enc["tag"])
    
    # 9. Lấy messages receiver
    status, msgs = get_messages(receiver_token, sender_id)  # ← SỬA Ở ĐÂY
    if status != 200:
        print("Failed to get messages")
        sys.exit(1)
    
    print("\n=== Messages Received ===")
    for msg in msgs:  # API trả về list
        try:
            aes_key_recv = unwrap_aes_key(msg["aes_key_encrypted"], receiver_priv)
            plaintext_recv = decrypt_aes_gcm(
    ciphertext_b64=msg["content"],
    iv_b64=msg["iv"],
    tag_b64=msg["tag"],
    key=aes_key_recv
)
            print(f"{msg['sender_id']} -> {msg['receiver_id']}: {plaintext_recv}")
        except Exception as e:
            print(f"Failed to decrypt messageđs: {e}")
if __name__ == "__main__":
    main()
