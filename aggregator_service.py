from flask import Flask
import requests
import asyncio
import aiohttp

aggregator_app = Flask(__name__)


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


# Actual Examples:
# This is a dummy sync method for customer profile:
@aggregator_app.route('/api/aggregate/<cus_id>')
def customer_profile(cus_id):
    # Synchronous calls to get data from all three microservices
    user_details = requests.get(f'http://127.0.0.1:8080/api/user/details/{cus_id}').json()
    order_details = requests.get(f'http://127.0.0.1:8081/api/orders/get/{cus_id}').json()
    payment_details = requests.get(f'http://127.0.0.1:8082/api/payments/find/{cus_id}').json()

    # Combine data into customer profile
    profile = {
        "UserDetails": user_details,
        "OrderHistory": order_details.get('orders', []),
        "PaymentHistory": payment_details.get('payments', [])
    }

    return profile


# This is a dummy async method for checkout process:
# New method for User! Needs implementation
async def fetch_user_details(session, cus_id):
    async with session.get(f'http://127.0.0.1:8080/api/user/details/{cus_id}') as response:
        return await response.text()


async def create_order(session):
    async with session.get('http://127.0.0.1:8081/api/orders/new') as response:
        return await response.text()


async def process_payment(session):
    async with session.get('http://127.0.0.1:8082/api/payment/pay') as response:
        return await response.text()


@aggregator_app.route('/api/aggregate/checkout/<cus_id>')
async def checkout(cus_id):
    async with aiohttp.ClientSession() as session:
        user_details = fetch_user_details(session, cus_id)
        order = create_order(session)
        payment = process_payment(session)
        # Wait and combine data to results in specific order for formatting
        results = await asyncio.gather(user_details, order, payment)

    checkout_info = (
        f"Checkout Information: <br>"
        f"UserDetails: {results[0]}<br>"
        f"Order Confirmation: {results[1]}<br>"
        f"Payment Process:{results[2]}")

    return checkout_info


if __name__ == '__main__':
    aggregator_app.run(host="127.0.0.1", port=8083, debug=True)
