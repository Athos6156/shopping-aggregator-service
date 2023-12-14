import json

from flask import Flask, request, jsonify
from db import DBUser
import mysql.connector
import urllib.request

user_app = Flask(__name__)
dbuser = DBUser()


# help functions
def get_user_info(data):
    userinfo = {}
    userinfo['username'] = data.get('username') if 'username' in data else ''
    userinfo['password'] = data.get('password') if 'password' in data else ''
    userinfo['first_name'] = data.get('first_name') if 'first_name' in data else ''
    userinfo['last_name'] = data.get('last_name') if 'last_name' in data else ''
    userinfo['address'] = data.get('address') if 'address' in data else ''
    userinfo['phone'] = data.get('phone') if 'phone' in data else ''
    userinfo['gender'] = data.get('gender') if 'gender' in data else ''
    return userinfo


@user_app.route('/')
def hello_world():
    return 'Hello World, I am the Users Service, I will handle users info!'


@user_app.route('/api/user/login/', methods=['POST'])
def login():
    data = request.get_json()
    user_info = get_user_info(data)

    connection = dbuser.connect_to_db()
    cursor = connection.cursor(dictionary=True)

    query = "SELECT * FROM dbuser WHERE username = %s AND password = %s"
    values = (user_info['username'], user_info['password'])

    cursor.execute(query, values)
    user = cursor.fetchone()

    cursor.close()
    connection.close()

    if user:
        return jsonify({'message': 'Login successful'})
    return jsonify({'message': 'Login failed'})


@user_app.route('/api/user/create/', methods=['POST'])
def create():
    data = request.get_json()
    user_info = get_user_info(data)

    connection = dbuser.connect_to_db()
    cursor = connection.cursor()

    # Check if the user already exists
    existing_user_query = "SELECT * FROM dbuser WHERE username = %s"
    cursor.execute(existing_user_query, (user_info['username'],))
    existing_user = cursor.fetchone()

    if existing_user:
        cursor.close()
        connection.close()
        return jsonify({'message': 'User with this username already exists'})

    # Create a new user
    create_user_query = (
        "INSERT INTO dbuser (username, password, first_name, last_name, address, phone, gender) VALUES "
        "(%s, %s, %s, %s, %s, %s, %s)")
    values = (
        user_info['username'],
        user_info['password'],
        user_info['first_name'],
        user_info['last_name'],
        user_info['address'],
        user_info['phone'],
        user_info['gender'],
    )

    try:
        url = f"https://us-street.api.smarty.com/street-address?street={user_info['address'].replace(' ', '+')}&auth-id=8d497be5-e211-4949-a18f-0bfd1d9970d3&auth-token=th4hargQiuyG7w7L7xfO"
        contents = urllib.request.urlopen(url).read()
        contents_json = json.loads(contents)
        if not contents_json:
            return jsonify({'message': 'Unable to verify address.'})
        else:
            address = contents_json[0]["delivery_line_1"] + ' ' + contents_json[0]["last_line"]
            values = (
                user_info['username'],
                user_info['password'],
                user_info['first_name'],
                user_info['last_name'],
                address,
                user_info['phone'],
                user_info['gender'],
            )
    except:
        return jsonify({'message': 'Unable to verify address.'})

    try:
        cursor.execute(create_user_query, values)
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({'message': 'User created successfully'})
    except mysql.connector.errors.IntegrityError as e:
        cursor.close()
        connection.close()
        return jsonify({'message': 'Error creating user. Username already exists.'})


@user_app.route('/api/user/update/', methods=['PUT'])
def update():
    data = request.get_json()
    user_info = get_user_info(data)

    connection = dbuser.connect_to_db()
    cursor = connection.cursor()

    # Check if the user exists
    existing_user_query = "SELECT * FROM dbuser WHERE username = %s"
    cursor.execute(existing_user_query, (user_info['username'],))
    existing_user = cursor.fetchone()

    if not existing_user:
        cursor.close()
        connection.close()
        return jsonify({'message': 'User not found'})

    # Update the user
    update_user_query = """
        UPDATE dbuser SET
        password = %s, first_name = %s, last_name = %s, address = %s, phone = %s, gender = %s
        WHERE username = %s
    """
    values = (
        user_info['password'], user_info['first_name'], user_info['last_name'], user_info['address'],
        user_info['phone'], user_info['gender'], user_info['username'],
    )

    try:
        cursor.execute(update_user_query, values)
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({'message': 'User updated successfully'})
    except mysql.connector.errors.IntegrityError as e:
        cursor.close()
        connection.close()
        return jsonify({'message': 'Error updating user. IntegrityError.'})


# ... (other imports)

@user_app.route('/api/user/delete/', methods=['DELETE'])
def delete():
    data = request.get_json()
    username = data.get('username')

    connection = dbuser.connect_to_db()
    cursor = connection.cursor()

    # Check if the user exists
    existing_user_query = "SELECT * FROM dbuser WHERE username = %s"
    cursor.execute(existing_user_query, (username,))
    existing_user = cursor.fetchone()

    if not existing_user:
        cursor.close()
        connection.close()
        return jsonify({'message': 'User not found'})

    # Delete the user
    delete_user_query = "DELETE FROM dbuser WHERE username = %s"
    values = (username,)

    try:
        cursor.execute(delete_user_query, values)
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({'message': 'User deleted successfully'})
    except mysql.connector.errors.IntegrityError as e:
        cursor.close()
        connection.close()
        return jsonify({'message': 'Error deleting user. IntegrityError.'})


if __name__ == '__main__':
    user_app.run(host="127.0.0.1", port=8080, debug=True)
