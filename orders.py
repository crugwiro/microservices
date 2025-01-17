from flask import Flask, jsonify, requests
import pika
import json

# Microservice 2: Order Service
order_service = Flask(__name__)

# Mock database for orders
orders = {
    1: {"id": 1, "user_id": 1, "item": "Dance Class Subscription", "price": 50},
    2: {"id": 2, "user_id": 2, "item": "Private Dance Lesson", "price": 100}
}

# RabbitMQ connection setup
def publish_event(event):
    print('in mq')
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='user_events')
    channel.basic_publish(exchange='', routing_key='user_events', body=json.dumps(event))
    connection.close()

@order_service.route('/orders', methods=['GET'])
def get_orders():
    return jsonify({"orders": list(orders.values())}), 200

@order_service.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = orders.get(order_id)
    if order:
        return jsonify(order), 200
    return jsonify({"error": "Order not found"}), 404

@order_service.route('/orders/user/<int:user_id>', methods=['GET'])
def get_orders_by_user(user_id):
    user_orders = [order for order in orders.values() if order["user_id"] == user_id]
    if user_orders:
        return jsonify({"orders": user_orders}), 200
    return jsonify({"error": "No orders found for this user"}), 404

@order_service.route('/orders/<int:order_id>/<int:user_id>', methods=['GET'])
def get_order_with_user(order_id, user_id):
    order = orders.get(order_id)
    print(f'getting user ${user_id}')
    if not order:
        return jsonify({"error": "Order not found"}), 404
    try:
        print(f'getting info user ${user_id}')
        user_response = requests.get(f'http://localhost:5001/users/{user_id}')
        if user_response.status_code == 200:
            user_data = user_response.json()
            order_with_user = {"order": order, "user": user_data}
            publish_event({"event": "order_with_user_retrieved", "order_id": order_id, "user": user_data})
            return jsonify(order_with_user), 200
        else:
            return jsonify({"error": "User not found"}), 404
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Failed to retrieve user data", "details": str(e)}), 500

if __name__ == '__main__':
    # Run with docker
    order_service.run(host='0.0.0.0', port=5002)