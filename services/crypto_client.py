# services/crypto_client.py
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes
import json
import os
from services import api_client  # Import để tự động đăng ký

def generate_rsa_keypair():
    key = RSA.generate(2048)
    return key.export_key().decode(), key.publickey().export_key().decode()

def generate_aes_key():
    return get_random_bytes(32)

def encrypt_aes_gcm(plaintext, key):
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode('utf-8'))
    return {
        "ciphertext": base64.b64encode(ciphertext).decode('utf-8'),
        "iv": base64.b64encode(cipher.nonce).decode('utf-8'),
        "tag": base64.b64encode(tag).decode('utf-8')
    }

def decrypt_aes_gcm(ciphertext_b64, iv_b64, tag_b64, key):
    try:
        ct = base64.b64decode(ciphertext_b64)
        nonce = base64.b64decode(iv_b64)
        tag = base64.b64decode(tag_b64)
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        pt = cipher.decrypt_and_verify(ct, tag)
        return pt.decode('utf-8')
    except ValueError as e:
        raise ValueError(f"Decrypt failed: {e}")

def wrap_aes_key(aes_key, public_key_pem):
    pub = RSA.import_key(public_key_pem)
    cipher = PKCS1_OAEP.new(pub, hashAlgo=SHA256)
    return base64.b64encode(cipher.encrypt(aes_key)).decode()

def unwrap_aes_key(wrapped_key_b64, private_key_pem):
    priv = RSA.import_key(private_key_pem)
    cipher = PKCS1_OAEP.new(priv, hashAlgo=SHA256)
    return cipher.decrypt(base64.b64decode(wrapped_key_b64))

def encrypt_private_key(private_key_pem, passphrase):
    salt = get_random_bytes(16)
    key = PBKDF2(passphrase, salt, dkLen=32, count=100_000, hmac_hash_module=SHA256)
    cipher = AES.new(key, AES.MODE_GCM)
    ct, tag = cipher.encrypt_and_digest(private_key_pem.encode('utf-8'))
    return {
        "ciphertext": base64.b64encode(ct).decode('utf-8'),
        "iv": base64.b64encode(cipher.nonce).decode('utf-8'),
        "tag": base64.b64encode(tag).decode('utf-8'),
        "salt": base64.b64encode(salt).decode('utf-8')
    }

def decrypt_private_key(enc_dict, passphrase):
    salt = base64.b64decode(enc_dict["salt"])
    key = PBKDF2(passphrase, salt, dkLen=32, count=100_000, hmac_hash_module=SHA256)
    nonce = base64.b64decode(enc_dict["iv"])
    tag = base64.b64decode(enc_dict["tag"])
    ct = base64.b64decode(enc_dict["ciphertext"])
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ct, tag).decode('utf-8')

def save_private_key(username: str, private_key_pem: str, password: str):
    enc = encrypt_private_key(private_key_pem, password)
    os.makedirs("keys", exist_ok=True)
    filepath = f"keys/{username}_private.enc.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(enc, f, indent=2)
    print(f"[INFO] Private key saved: {filepath}")

def load_private_key(username: str, password: str) -> str:
    filepath = f"keys/{username}_private.enc.json"
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Private key not found: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        enc = json.load(f)
    return decrypt_private_key(enc, password)

# MỚI: Tự động sinh key + đăng ký + lưu
def register_and_save_key(username: str, password: str):
    private_pem, public_pem = generate_rsa_keypair()
    print(f"[KEY] Generated RSA key pair for {username}")

    status, data = api_client.register(username, password, public_pem)
    if status != 201:
        raise Exception(f"Register failed: {data.get('msg')}")

    save_private_key(username, private_pem, password)
    print(f"[KEY] Private key encrypted and saved")
    return private_pem, public_pem