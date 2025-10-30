from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models.message import Message

chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/send", methods=["POST"])
@jwt_required()
def send_message():
    data = request.get_json()
    
    # Danh sách bắt buộc
    required_fields = ["receiver_id", "content", "aes_key_encrypted", "iv", "tag"]
    for field in required_fields:
        if field not in data:
            return jsonify({"msg": f"Missing field: {field}"}), 400

    sender_id = int(get_jwt_identity())
    receiver_id = data["receiver_id"]
    content = data["content"]
    aes_key_encrypted = data["aes_key_encrypted"]
    iv = data["iv"]      # Không dùng .get()
    tag = data["tag"]    # Không dùng .get()

    msg = Message(
        sender_id=sender_id,
        receiver_id=receiver_id,
        content=content,
        aes_key_encrypted=aes_key_encrypted,
        iv=iv,
        tag=tag
    )
    db.session.add(msg)
    db.session.commit()
    return jsonify({"msg": "Message sent"}), 200

@chat_bp.route("/messages/<int:user_id>", methods=["GET"])
@jwt_required()
def get_messages(user_id):
    me = int(get_jwt_identity())
    messages = Message.query.filter(
        ((Message.sender_id == me) & (Message.receiver_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.receiver_id == me))
    ).order_by(Message.timestamp.asc()).all()

    return jsonify([{
        "id": m.id,
        "sender_id": m.sender_id,
        "receiver_id": m.receiver_id,
        "content": m.content,
        "aes_key_encrypted": m.aes_key_encrypted,
        "iv": m.iv,
        "tag": m.tag,
        "timestamp": m.timestamp.isoformat()
    } for m in messages])
