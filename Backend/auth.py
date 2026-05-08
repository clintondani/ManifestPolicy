from flask import Blueprint, request, jsonify
import json, os, hashlib

auth_bp = Blueprint("auth", __name__)

DATABASE_FILE = "database.json"

def read_db():
    if not os.path.exists(DATABASE_FILE):
        return {"users": []}
    with open(DATABASE_FILE, "r") as f:
        return json.load(f)

def write_db(data):
    with open(DATABASE_FILE, "w") as f:
        json.dump(data, f, indent=4)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    db = read_db()
    if any(u["username"] == username for u in db["users"]):
        return jsonify({"error": "User already exists"}), 400

    new_user = {
        "username": username,
        "password": hash_password(password),
        "history": []
    }
    db["users"].append(new_user)
    write_db(db)

    return jsonify({"message": "Signup successful!"}), 200


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    db = read_db()
    user = next((u for u in db["users"] if u["username"] == username), None)

    if not user or user["password"] != hash_password(password):
        return jsonify({"error": "Invalid username or password"}), 401

    return jsonify({"message": "Login successful", "username": username}), 200
