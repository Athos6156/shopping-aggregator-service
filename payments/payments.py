import urllib.request
import os

import mysql.connector
from flask import Flask, request, jsonify
from flask import Flask
from db import DBUser
import json
import boto3

app = Flask("Payments")
dbuser = DBUser()


@app.route('/')
def hello_world():
    return 'Hello World, I am the payments service. Wheres your money?!'


@app.route('/api/payment/pay', methods=['POST'])
def accept_payment():
    data = request.get_json()
    api_key = '27bd20c1-30b0-48eb-8b4f-1ccf51134d57'

    card_num = data['payment_method']
    order_id = data['order_id']
    amount = data['amount']
    status = 1

    url = f'https://api.apistacks.com/v1/validatecard?api_key={api_key}&cardnumber={card_num}'
    try:
        contents = json.loads(urllib.request.urlopen(url).read())
        if contents['status'] == 'ok':
            payment_query = ("INSERT INTO payments (order_id, status, amount, payment_method)"
                             " VALUES (%s, %s, %s, %s)")
            values = (
                order_id,
                status,
                amount,
                card_num)
            connection = dbuser.connect_to_db()
            cursor = connection.cursor()
            try:
                cursor.execute(payment_query, values)
                connection.commit()
                cursor.close()
                connection.close()

                client = boto3.client("sns", aws_access_key_id=os.environ.get('aws_key'),
                                      aws_secret_access_key=os.environ.get('secret_key'))
                # TODO - move this to the aggregator service, it can fetch the user info to form the email
                message = {'recipient': 'kg2982@columbia.edu', 'subject': 'Athos Payment Notification',
                           'body': f'Payment for Amount{amount} processed successfully'}
                try:
                    client.publish(TargetArn='arn:aws:sns:us-east-1:114811598002:karthikguda-email-deliv',
                                   Message=json.dumps(message))
                except Exception as e:
                    print(e)

                return jsonify({'message': 'paid successfully'})
            except mysql.connector.errors.IntegrityError as e:
                cursor.close()
                connection.close()
                return jsonify({'message': 'Error processing payment. Invalid card'})
        else:
            return jsonify({'message': 'Error processing payment. Invalid card'})
    except:
        return jsonify({'message': 'Unable to verify payment.'})


@app.route('/api/payment/refund', methods=['POST'])
def refund_payment():
    data = request.get_json()
    order_id = data['order_id']
    connection = dbuser.connect_to_db()
    cursor = connection.cursor()

    try:
        payment_query = f"update payments set refunded=1 where order_id='{order_id}' ;"
        cursor.execute(payment_query)
        connection.commit()
        return jsonify({'message': 'Refunded'})
    except:
        cursor.close()
        connection.close()
        return jsonify({'message': 'Error processing refund.'})


@app.route('/api/payment/find', methods=['POST'])
def find_payment():
    data = request.get_json()
    order_id = data['order_id']
    connection = dbuser.connect_to_db()
    cursor = connection.cursor()

    try:
        payment_query = f"select * from payments where order_id=\'{order_id}\'"
        cursor.execute(payment_query)
        order_payment = cursor.fetchone()
        if order_payment:
            return jsonify({'order_id': order_payment[0], 'refunded': order_payment[1], 'id': order_payment[2],
                            'status': order_payment[3], 'amount': order_payment[4], 'payment_method': order_payment[5]})
    except:
        cursor.close()
        connection.close()
        return jsonify({'message': 'Error finding order payment'})


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8082, debug=True)
