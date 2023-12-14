from flask import Flask, jsonify, request
import requests
import asyncio
import aiohttp

aggregator_app = Flask(__name__)

@aggregator_app.route('/')
def hello_world():
    return 'Hello World, I am the Aggregator Service, I will aggregate your requests!'

@aggregator_app.route('/api/aggregate/sync_test')
def aggregate_sync_test():
    user_service_response = requests.get('http://127.0.0.1:8080/api/user/login/')
    order_service_response = requests.get('http://127.0.0.1:8081/api/orders/get')
    payment_service_response = requests.get('http://127.0.0.1:8082/api/payment/find')

    return (f"This is a test of synchronous call<br>"
            f"User Service: {user_service_response.text}<br>"
            f"Order Service: {order_service_response.text}<br>"
            f"Payment Service: {payment_service_response.text}")


async def fetch(session, addr):
    async with session.get(addr) as response:
        return await response.text()


async def aggregate_async_test():
    addrs = [
        'http://127.0.0.1:8080/api/user/login/',
        'http://127.0.0.1:8081/api/orders/get',
        'http://127.0.0.1:8082/api/payment/find'
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
    user_response = requests.post('http://127.0.0.1:8080/api/user/create/', json=user_data)
    if user_response.status_code != 200:
        # If user creation fails, return the response
        return user_response.json(), user_response.status_code

    # Assume same username
    order_data['username'] = user_data['username']

    # Create Order
    order_response = requests.post('http://127.0.0.1:8081/api/order/create/', json=order_data)
    if order_response.status_code != 200:
        # If order creation fails, return the response
        return order_response.json(), order_response.status_code

    # Process payment
    payment_response = requests.post('http://127.0.0.1:8082/api/payment/pay', json=payment_data)
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
    order_response = requests.post('http://127.0.0.1:8081/api/order/create/', json=order_data)
    if order_response.status_code != 200:
        return order_response.json(), order_response.status_code

    # Process payment
    payment_response = requests.post('http://127.0.0.1:8082/api/payment/pay', json=payment_data)
    if payment_response.status_code != 200:
        # If payment creation fails, return the response
        return payment_response.json(), payment_response.status_code

    # Response
    order_message = order_response.json().get('message')
    payment_message = payment_response.json().get('message')
    aggregated_message = f"Order Service: {order_message}; Payment Service: {payment_message}"
    return jsonify({'message': aggregated_message})



# delete+refund service, synced
# refund service not working, need help
@aggregator_app.route('/api/aggregate/delete_refund', methods=['POST'])
def delete_refund():
    data = request.get_json()
    order_data = data['order']
    payment_data = data['payment']

    # Delete order
    order_response = requests.delete('http://127.0.0.1:8081/api/order/delete/', json=order_data)
    if not order_response.ok:
        return order_response.json(), order_response.status_code

    # Refund payment
    refund_response = requests.post('http://127.0.0.1:8082/api/payment/refund', json=payment_data)
    if refund_response.status_code != 200:
        # If payment creation fails, return the response
        return refund_response.json(), refund_response.status_code

    # Response
    order_message = order_response.json().get('message')
    refund_message = refund_response.json().get('message')
    aggregated_message = f"Order Service: {order_message}; Payment Service: {refund_message}"
    return jsonify({'message': aggregated_message})


if __name__ == '__main__':
    aggregator_app.run(host="127.0.0.1", port=8083, debug=True)
