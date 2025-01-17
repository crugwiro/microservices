from flask import Flask, jsonify, request

# Microservice 1: User Service
user_service = Flask(__name__)

# Mock database for users
users = {
    1: {"id": 1, "name": "Alice", "email": "alice@example.com"},
    2: {"id": 2, "name": "Bob", "email": "bob@example.com"}
}

@user_service.route('/users', methods=['GET'])
def get_users():
    return jsonify({"users": list(users.values())}), 200

@user_service.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = users.get(user_id)
    if user:
        return jsonify(user), 200
    return jsonify({"error": "User not found"}), 404


if __name__ == '__main__':
    # Run
    user_service.run(host='0.0.0.0', port=5001)