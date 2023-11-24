from flask import Flask, jsonify

users_app = Flask(__name__)


# TODO - move this into a class

@users_app.route('/api/user/login/')
def login():
    return 'Hello World, I am the Users Service, I will "handle" users :D !'


@users_app.route('/api/user/create/')
def create():
    return 'Hello World, I am the Users Service, I will "handle" users :D !'


@users_app.route('/api/user/update/')
def update():
    return 'Hello World, I am the Users Service, I will "handle" users :D !'


@users_app.route('/api/user/delete/')
def delete():
    return 'Hello World, I am the Users Service, I will "handle" users :D !'


# Dummy

@users_app.route('/api/user/details/<cus_id>')
def user_details(cus_id):
    # Generate dummy user details
    return jsonify({
        "customer_id": cus_id,
        "name": "Shen Gao",
        "email": "sg4140@columbia.edu"
    })


if __name__ == '__main__':
    users_app.run(host="127.0.0.1", port=8080, debug=True)
