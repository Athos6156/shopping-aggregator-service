from flask import Flask, jsonify

payments_app = Flask("Payments")


@payments_app.route('/')
def hello_world():
	return 'Hello World, I am the payments service. Wheres your money?!'


@payments_app.route('/api/payment/pay')
def accept_payment():
	return jsonify({
		"payment_id": "P123456789",
		"status": "Processed",
		"amount": "100.00",
		"confirmation": "CONFIRMED"
	})


@payments_app.route('/api/payment/refund')
def refund_payment():
	return 'Hello World, I am the payments service. Wheres your money?!'


@payments_app.route('/api/payment/find')
def find_payment():
	return 'Hello World, I am the payments service. Wheres your money?!'


if __name__ == '__main__':
	payments_app.run(host="127.0.0.1", port=8082, debug=True)