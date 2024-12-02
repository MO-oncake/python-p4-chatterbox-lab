from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from flask_migrate import Migrate
from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        messages = Message.query.order_by(Message.created_at.asc()).all()
        return jsonify([message.to_dict() for message in messages])

    elif request.method == 'POST':
        data = request.get_json()
        body = data.get('body')
        username = data.get('username')

        if not body or not username:
            return make_response({'error': 'Body and username are required'}, 400)

        new_message = Message(body=body, username=username)
        db.session.add(new_message)
        db.session.commit()
        return jsonify(new_message.to_dict()), 201


@app.route('/messages/<int:id>', methods=['PATCH', 'DELETE'])
def message_by_id(id):
    message = Message.query.get(id)
    if not message:
        return make_response({'error': 'Message not found'}, 404)

    if request.method == 'PATCH':
        data = request.get_json()
        body = data.get('body')
        if not body:
            return make_response({'error': 'Body is required'}, 400)

        message.body = body
        db.session.commit()
        return jsonify(message.to_dict())

    elif request.method == 'DELETE':
        db.session.delete(message)
        db.session.commit()
        return make_response({'message': 'Message deleted successfully'}, 200)


if __name__ == '__main__':
    app.run(port=5555)
