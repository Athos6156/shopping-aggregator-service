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


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


async def aggregate_async_test():
    async with aiohttp.ClientSession() as session:
        user_service = fetch(session, 'http://127.0.0.1:8080/api/user/login/')
        order_service = fetch(session, 'http://127.0.0.1:8081/api/orders/get')
        payment_service = fetch(session, 'http://127.0.0.1:8082/api/payment/find')

        responses = await asyncio.gather(user_service, order_service, payment_service)

        return (f"This is a test of asynchronous call<br>"
                f"User Service: {responses[0]}<br>"
                f"Order Service: {responses[1]}<br>"
                f"Payment Service: {responses[2]}")


@aggregator_app.route('/api/aggregate/async_test')
def aggregate_async_execute():
    return asyncio.run(aggregate_async_test())


if __name__ == '__main__':
    aggregator_app.run(host="127.0.0.1", port=8083, debug=True)
