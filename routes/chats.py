from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import Chat, ChatMember, Account

chats_bp = Blueprint("chats", __name__)

@chats_bp.route("", methods=["POST"])
@jwt_required()
def create_chat():
    data = request.get_json()
    name = data.get("name")
    is_group = data.get("is_group", False)
    members = data.get("members", [])

    if not is_group and len(members) != 1:
        return jsonify({"msg": "1-1 chat requires exactly 1 member"}), 400

    # Kiểm tra các user_id hợp lệ
    valid_members = []
    for m in members:
        if Account.query.get(m):
            valid_members.append(m)

    chat = Chat(name=name, is_group=is_group)
    db.session.add(chat)
    db.session.commit()

    creator_id = int(get_jwt_identity())
    db.session.add(ChatMember(chat_id=chat.id, account_id=creator_id))
    for m in valid_members:
        if m != creator_id:
            db.session.add(ChatMember(chat_id=chat.id, account_id=m))
    db.session.commit()

    return jsonify({"msg": "Chat created", "chat_id": chat.id}), 201

@chats_bp.route("", methods=["GET"])
@jwt_required()
def get_chats():
    user_id = int(get_jwt_identity())
    memberships = ChatMember.query.filter_by(account_id=user_id).all()
    chats = []
    for m in memberships:
        chat = m.chat
        chats.append({
            "chat_id": chat.id,
            "name": chat.name,
            "is_group": chat.is_group,
            "members": [cm.account_id for cm in chat.members],
            "created_at": chat.created_at.isoformat()
        })
    return jsonify(chats)
@chats_bp.route("/<int:chat_id>", methods=["GET"])
@jwt_required()
def get_chat_detail(chat_id):
    user_id = int(get_jwt_identity())
    chat = Chat.query.get(chat_id)
    if not chat:
        return jsonify({"msg": "Chat not found"}), 404

    # Kiểm tra user có nằm trong chat không
    membership = ChatMember.query.filter_by(chat_id=chat_id, account_id=user_id).first()
    if not membership:
        return jsonify({"msg": "You are not a member of this chat"}), 403

    return jsonify({
        "chat_id": chat.id,
        "name": chat.name,
        "is_group": chat.is_group,
        "members": [cm.account_id for cm in chat.members],
        "created_at": chat.created_at.isoformat()
    }), 200