from secrets import token_hex

from flask import Flask, render_template, request, redirect, flash, make_response, abort, jsonify, Response

from config import database_uri
from models import db, User, Session, Offer
import hashlib

app = Flask(__name__, static_url_path='',
            static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
db.init_app(app)

app.secret_key = 'sparks_key'


def password_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()


@app.route('/', methods=['GET'])
def main_page():
    token = request.cookies.get('session_token')

    if token is not None:
        session = Session.query.filter(Session.token == token).first()
        if session is not None:
            return render_template('main.html', username=session.user.username)

    return redirect('/auth')


@app.route('/auth', methods=['GET'])
def auth_page():
    return render_template('auth.html')


@app.route('/auth', methods=['POST'])
def log_in():
    username = request.form['username']
    password = request.form['password']

    # db.session.add(User(username=username, password=password_hash(password)))
    # db.session.commit()

    user = User.query.filter(User.username == username, User.password == password_hash(password)).first()

    if user is not None:
        token = token_hex(16)

        session = Session(
            user_id=user.id,
            token=token
        )

        db.session.add(session)
        db.session.commit()

        response = make_response(redirect('/'))
        response.set_cookie('session_token', token)

        return response

    else:
        flash('Неверный логин или пароль')
        return redirect('/auth')


@app.route('/logout', methods=['POST'])
def log_out():
    response = make_response(redirect('/'))
    response.delete_cookie('session_token')

    return response


@app.route('/get_content', methods=['POST'])
def get_content():
    token = request.cookies.get('session_token')

    order_by = Offer.id

    sort = int(request.form['sort'])

    if sort == 1:
        order_by = Offer.price
    elif sort == 2:
        order_by = Offer.price.desc()

    if token is not None:
        session = Session.query.filter(Session.token == token).first()
        if session is not None:
            return jsonify(
                {
                    "access_level": session.user.access_level,
                    "offers": [
                        {
                            "id": offer.id,
                            "name": offer.name,
                            "seller_name": offer.seller_name if session.user.access_level >= 3 else None,
                            "price": offer.price,
                            "img_link": offer.image_link if session.user.access_level >= 2 else None
                        } for offer in
                        Offer.query.filter_by(is_active=True).filter(
                            Offer.price.isnot(None)
                        ).order_by(order_by).limit(
                            session.user.access_level * 100).all()
                    ]
                }
            )

    abort(401)


@app.route('/delete_offer', methods=['POST'])
def delete_offer():
    token = request.cookies.get('session_token')

    offer_id = int(request.form['offer_id'])

    if token is not None:
        session = Session.query.filter(Session.token == token).first()
        if session is not None:
            Offer.query.filter_by(id=offer_id).delete()
            db.session.commit()

            return Response(status=200)

    abort(401)


if __name__ == '__main__':
    app.run()
