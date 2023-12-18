from aiohttp import ClientSession, ClientConnectionError, ContentTypeError
from flask import Flask, jsonify, request
import requests
import asyncio
import aiohttp

aggregator_app = Flask(__name__)


# User: http://ec2-107-22-87-117.compute-1.amazonaws.com:5002/
# Order: http://ec2-107-22-87-117.compute-1.amazonaws.com:5003/
# Payment: http://ec2-107-22-87-117.compute-1.amazonaws.com:5001/

@aggregator_app.route('/')
def hello_world():
    return 'Hello World, I am the Aggregator Service, I will aggregate your requests!'


@aggregator_app.route('/api/aggregate/sync_test')
def aggregate_sync_test():
    user_service_response = requests.get('http://ec2-107-22-87-117.compute-1.amazonaws.com:5002/api/user/login/')
    order_service_response = requests.get('http://ec2-107-22-87-117.compute-1.amazonaws.com:5003/api/orders/get')
    payment_service_response = requests.get('http://ec2-107-22-87-117.compute-1.amazonaws.com:5001/api/payment/find')

    return (f"This is a test of synchronous call<br>"
            f"User Service: {user_service_response.text}<br>"
            f"Order Service: {order_service_response.text}<br>"
            f"Payment Service: {payment_service_response.text}")


async def fetch(session, addr):
    async with session.get(addr) as response:
        return await response.text()


async def aggregate_async_test():
    addrs = [
        'http://ec2-107-22-87-117.compute-1.amazonaws.com:5002/api/user/login/',
        'http://ec2-107-22-87-117.compute-1.amazonaws.com:5003/api/orders/get',
        'http://ec2-107-22-87-117.compute-1.amazonaws.com:5001/api/payment/find'
    ]
    results = []

    async with aiohttp.ClientSession() as session:
        gets = [fetch(session, addr) for addr in addrs]
        # Append data to results by first-come-first-serve order
        for future in asyncio.as_completed(gets):
            result = await future
            results.append(result)

    return results


@aggregator_app.route('/api/aggregate/async_test')
def aggregate_async_execute():
    result = asyncio.run(aggregate_async_test())
    return (f"This is a test of asynchronous call<br>"
            f"{result[0]}<br>"
            f"{result[1]}<br>"
            f"{result[2]}")


# register+order+pay service, synced
@aggregator_app.route('/api/aggregate/register_order_pay', methods=['POST'])
def register_order_pay():
    data = request.get_json()
    user_data = data['user']
    order_data = data['order']
    payment_data = data['payment']

    # Create User
    user_response = requests.post('http://ec2-107-22-87-117.compute-1.amazonaws.com:5002/api/user/create/',
                                  json=user_data)
    if user_response.status_code != 200:
        # If user creation fails, return the response
        return user_response.json(), user_response.status_code

    # Assume same username
    order_data['username'] = user_data['username']

    # Create order
    order_response = requests.post('http://ec2-107-22-87-117.compute-1.amazonaws.com:5003/api/order/create/',
                                   json=order_data)
    if order_response.status_code != 200:
        return order_response.json(), order_response.status_code

    # Process payment
    payment_response = requests.post('http://ec2-107-22-87-117.compute-1.amazonaws.com:5001/api/payment/pay',
                                     json=payment_data)
    if payment_response.status_code != 200:
        # If payment creation fails, return the response
        return payment_response.json(), payment_response.status_code

    # Response
    user_message = user_response.json().get('message')
    order_message = order_response.json().get('message')
    payment_message = payment_response.json().get('message')
    aggregated_message = f"User Service: {user_message}; Order Service: {order_message}; Payment Service: {payment_message}"
    return jsonify({'message': aggregated_message})


# order+pay service, synced
@aggregator_app.route('/api/aggregate/order_pay', methods=['POST'])
def order_pay():
    data = request.get_json()
    order_data = data['order']
    payment_data = data['payment']

    # Create order
    order_response = requests.post('http://ec2-107-22-87-117.compute-1.amazonaws.com:5003/api/order/create/',
                                   json=order_data)
    if order_response.status_code != 200:
        return order_response.json(), order_response.status_code

    # Process payment
    payment_response = requests.post('http://ec2-107-22-87-117.compute-1.amazonaws.com:5001/api/payment/pay',
                                     json=payment_data)
    if payment_response.status_code != 200:
        # If payment creation fails, return the response
        return payment_response.json(), payment_response.status_code

    # Response
    order_message = order_response.json().get('message')
    payment_message = payment_response.json().get('message')
    aggregated_message = f"Order Service: {order_message}; Payment Service: {payment_message}"
    return jsonify({'message': aggregated_message})


# async def fetch_post(session, url, json_data):
#    try:
#        async with session.post(url, json=json_data) as response:
#            return await response.json(), response.status
#    except (ClientConnectionError, TimeoutError, ContentTypeError):
#        return {'message': 'Failed to reach service.'}, 404

async def fetch_post(session, url, json_data, service_name):
    try:
        async with session.post(url, json=json_data) as response:
            data = await response.json()
            message = data.get('message')
            return f"{service_name} Service: {message}", response.status
    except (ClientConnectionError, TimeoutError, ContentTypeError):
        return f"Failed to reach {service_name} service.", 404


async def order_payment_middle(order_data, payment_data, order_url, payment_url):
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_post(session, order_url, order_data, "Order"),
            fetch_post(session, payment_url, payment_data, "Payment")
        ]

        messages = []
        for future in asyncio.as_completed(tasks):
            message, status = await future
            if status != 200:
                return {'message': message}, status
            messages.append(message)

        aggregated_message = "; ".join(messages)
        return {'message': aggregated_message}, 200


# order+pay service, asynced
@aggregator_app.route('/api/aggregate/order_pay_async', methods=['POST'])
async def order_pay_async():
    order_url = 'http://ec2-107-22-87-117.compute-1.amazonaws.com:5003/api/order/create/'
    payment_url = 'http://ec2-107-22-87-117.compute-1.amazonaws.com:5001/api/payment/pay'

    data = request.get_json()
    order_data = data['order']
    payment_data = data['payment']

    # Create order + Process payment
    response, status = await order_payment_middle(order_data, payment_data, order_url, payment_url)
    return jsonify(response), status


# delete+refund service, synced
# refund service not working, need help
@aggregator_app.route('/api/aggregate/delete_refund', methods=['POST'])
def delete_refund():
    data = request.get_json()
    order_data = data['order']
    payment_data = data['payment']

    # Delete order
    order_response = requests.delete('http://ec2-107-22-87-117.compute-1.amazonaws.com:5003/api/order/delete/',
                                     json=order_data)
    if not order_response.ok:
        return order_response.json(), order_response.status_code

    # Refund payment
    refund_response = requests.post('http://ec2-107-22-87-117.compute-1.amazonaws.com:5001/api/payment/refund',
                                    json=payment_data)
    if refund_response.status_code != 200:
        # If payment creation fails, return the response
        return refund_response.json(), refund_response.status_code

    # Response
    order_message = order_response.json().get('message')
    refund_message = refund_response.json().get('message')
    aggregated_message = f"Order Service: {order_message}; Payment Service: {refund_message}"
    return jsonify({'message': aggregated_message})


# delete+refund service, asynced
@aggregator_app.route('/api/aggregate/delete_refund_async', methods=['POST'])
async def delete_refund_async():
    order_url = 'http://ec2-107-22-87-117.compute-1.amazonaws.com:5003/api/order/delete/'
    payment_url = 'http://ec2-107-22-87-117.compute-1.amazonaws.com:5001/api/payment/refund'

    data = request.get_json()
    order_data = data['order']
    payment_data = data['payment']

    # Delete order + Refund payment
    response, status = await order_payment_middle(order_data, payment_data, order_url, payment_url)
    return jsonify(response), status


if __name__ == '__main__':
    aggregator_app.run(host="127.0.0.1", port=8083, debug=True)
