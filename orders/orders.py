from flask import Flask, request, jsonify
from db import DBUser
import mysql.connector

order_app = Flask(__name__)
dborder = DBUser()


# help functions
def get_order_info(data):
    orderinfo = {}
    orderinfo['username'] = data.get('username') if 'username' in data else ''
    orderinfo['id'] = data.get('id') if 'id' in data else ''
    orderinfo['order_date'] = data.get('order_date') if 'order_date' in data else ''
    orderinfo['status'] = data.get('status') if 'status' in data else ''
    orderinfo['order_num'] = data.get('order_num') if 'order_num' in data else ''
    orderinfo['ship_num'] = data.get('ship_num') if 'ship_num' in data else ''
    return orderinfo


@order_app.route('/')
def hello_world():
    return 'Hello World, I am the Orders Service, I will handle orders info!'


@order_app.route('/api/order/create/', methods=['POST'])
def create():
    data = request.get_json()
    order_info = get_order_info(data)
    connection = dborder.connect_to_db()
    cursor = connection.cursor()

    # Check if the order already exists
    existing_order_query = "SELECT * FROM dborder WHERE id = %s"
    cursor.execute(existing_order_query, (order_info['order_num'],))
    existing_order = cursor.fetchone()

    if existing_order:
        cursor.close()
        connection.close()
        return jsonify({'message': 'Order already exists'})

    # Create a new order
    create_order_query = "INSERT INTO dborder (username, status, ship_num) VALUES (%s,  %s, %s)"
    values = (
        order_info['username'],
        order_info['status'],
        order_info['ship_num'],
    )

    try:
        cursor.execute(create_order_query, values)
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({'message': 'Order placed successfully'})
    except mysql.connector.errors.IntegrityError as e:
        cursor.close()
        connection.close()
        return jsonify({'message': 'Error placing order.'})


@order_app.route('/api/order/update/', methods=['PUT'])
def update():
    data = request.get_json()
    order_info = get_order_info(data)

    connection = dborder.connect_to_db()
    cursor = connection.cursor()

    # Check if the order exists
    existing_order_query = f"SELECT * FROM dborder WHERE id = {int(order_info['id'])};"
    cursor.execute(existing_order_query)
    existing_order = cursor.fetchone()

    if not existing_order:
        cursor.close()
        connection.close()
        return jsonify({'message': 'Order not found'})

    # Update the order
    update_order_query = f"""
		UPDATE dborder SET
		status = %s, ship_num = %s
		WHERE id = {int(order_info['id'])};
    """

    values = (
        order_info['status'],
        order_info['ship_num'],
    )

    try:
        cursor.execute(update_order_query, values)
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({'message': 'User updated successfully'})
    except mysql.connector.errors.IntegrityError as e:
        cursor.close()
        connection.close()
        return jsonify({'message': 'Error updating user. IntegrityError.'})


# ... (other imports)

@order_app.route('/api/order/delete/', methods=['DELETE'])
def delete():
    data = request.get_json()
    ordernum = data.get('order_num')
    order_info = get_order_info(data)
    connection = dborder.connect_to_db()
    cursor = connection.cursor()

    # Check if the order exists
    existing_order_query = "SELECT * FROM dborder WHERE order_num = %s"
    cursor.execute(existing_order_query, (order_info['order_num'],))
    existing_order = cursor.fetchone()

    if not existing_order:
        cursor.close()
        connection.close()
        return jsonify({'message': 'Order not found'})

    # Delete the order
    delete_order_query = "DELETE FROM dborder WHERE order_num = %s"
    values = (ordernum,)

    try:
        cursor.execute(delete_order_query, values)
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({'message': 'Order cancelled successfully'})
    except mysql.connector.errors.IntegrityError as e:
        cursor.close()
        connection.close()
        return jsonify({'message': 'Error cancelling order. IntegrityError.'})


if __name__ == '__main__':
    order_app.run(host="127.0.0.1", port=8081, debug=True)
