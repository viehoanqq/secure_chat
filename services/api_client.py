# services/api_client.py
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def register(username, password, public_key):
    print(f"[DEBUG] Registering user: {username}")
    try:
        r = requests.post(f"{BASE_URL}/auth/register", json={
            "username": username,
            "password": password,
            "public_key": public_key
        })
        print(f"[DEBUG] Register response: {r.status_code}, {r.text}")
        try:
            data = r.json()
        except json.JSONDecodeError:
            data = {"msg": r.text}
        return r.status_code, data
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Register request failed: {e}")
        return None, {"msg": str(e)}

def login(username, password):
    print(f"[DEBUG] Logging in user: {username}")
    try:
        r = requests.post(f"{BASE_URL}/auth/login", json={
            "username": username,
            "password": password
        })
        print(f"[DEBUG] Login response: {r.status_code}, {r.text}")
        try:
            data = r.json()
        except json.JSONDecodeError:
            data = {"msg": r.text}
        token = data.get("token")
        user_id = data.get("user_id")
        return token, user_id, data
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Login request failed: {e}")
        return None, None, {"msg": str(e)}

def get_user_info(token, user_id):
    print(f"[DEBUG] Getting user info for ID: {user_id}")
    try:
        r = requests.get(f"{BASE_URL}/auth/user/{user_id}",
                        headers={"Authorization": f"Bearer {token}"})
        print(f"[DEBUG] Get user response: {r.status_code}, {r.text}")
        try:
            data = r.json()
        except json.JSONDecodeError:
            data = {"msg": r.text}
        return r.status_code, data
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Get user request failed: {e}")
        return None, {"msg": str(e)}

def send_message(token, receiver_id, content, aes_key_encrypted, iv, tag):
    print(f"[DEBUG] Sending message to {receiver_id}")
    payload = {
        "receiver_id": receiver_id,
        "content": content,
        "aes_key_encrypted": aes_key_encrypted,
        "iv": iv,
        "tag": tag
    }
    try:
        r = requests.post(f"{BASE_URL}/chat/send",
                          headers={"Authorization": f"Bearer {token}"},
                          json=payload)
        print(f"[DEBUG] Send message response: {r.status_code}, {r.text}")
        try:
            data = r.json()
        except json.JSONDecodeError:
            data = {"msg": r.text}
        return r.status_code, data
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Send message request failed: {e}")
        return None, {"msg": str(e)}

def get_messages(token, user_id):
    print(f"[DEBUG] Getting messages for user ID: {user_id}")
    try:
        r = requests.get(f"{BASE_URL}/chat/messages/{user_id}",
                         headers={"Authorization": f"Bearer {token}"})
        print(f"[DEBUG] Get messages response: {r.status_code}, {r.text}")
        try:
            data = r.json()
        except json.JSONDecodeError:
            data = {"msg": r.text}
        return r.status_code, data
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Get messages request failed: {e}")
        return None, {"msg": str(e)}
