from flask import Flask, jsonify
orders_app = Flask(__name__)


@orders_app.route('/')
def hello_world():
    return 'Hello World, I am the Orders Service, I will handle orders!'


@orders_app.route('/api/orders/new')
def new_order():
    return jsonify({
        "order_id": "O123456789",
        "status": "Created",
        "items": "Some Stuff",
        "price": 100.00
    })


@orders_app.route('/api/orders/update')
def update_order():
    return 'Hello World, I am the Orders Service, I will handle orders!'


@orders_app.route('/api/orders/get')
def get_order():
    return 'Hello World, I am the Orders Service, I will handle orders!'


@orders_app.route('/api/orders/delete')
def delete_order():
    return 'Hello World, I am the Orders Service, I will handle orders!'


if __name__ == '__main__':
    orders_app.run(host="127.0.0.1", port=8081, debug=True)
