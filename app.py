from flask import Flask, render_template, jsonify, request, session, redirect, url_for

app = Flask(__name__)

from pymongo import MongoClient

import certifi
import jwt
import datetime
import hashlib
import requests

client = MongoClient('mongodb+srv://test:sparta@cluster0.ke58o.mongodb.net/cluster0?retryWrites=true&w=majority',tlsCAFile=certifi.where())
db = client.dbsparta_plus_week4

SECRET_KEY = 'ASD'

@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"id": payload['id']})
        return render_template('index.html', nickname=user_info["nick"])
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login"))

@app.route("/cocktail", methods=["POST"])
def comment_post():
    index_receive = request.form['index_give']
    comment_receive = request.form['comment_give']
    nick_receive = request.form['nick_give']
    doc = {
        'nick': nick_receive,
        'index': index_receive,
        'comment': comment_receive
    }
    db.cocktail.insert_one(doc)
    return jsonify({'msg': '저장완료 !'})

@app.route("/cocktail", methods=["GET"])
def comment_get():
    comment = list(db.cocktail.find({}, {'_id': False}))
    return jsonify({'comment': comment})

@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/api/register', methods=['POST'])
def api_register():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    nickname_receive = request.form['nickname_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    db.user.insert_one({'id': id_receive, 'pw': pw_hash, 'nick': nickname_receive})

    return jsonify({'result': 'success'})


@app.route('/api/login', methods=['POST'])
def api_login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
    result = db.user.find_one({'id': id_receive, 'pw': pw_hash})

    if result is not None:
        payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds= 60 * 60 *24)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/review/<keyword>')
def review(keyword):
  r = requests.get(f"https://www.thecocktaildb.com/api/json/v1/1/filter.php?g=Cocktail_glass")
  result = r.json()
  cockid = result
  token_receive = request.cookies.get('mytoken')
  payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
  user_info = db.user.find_one({"id": payload['id']})
  for i in cockid['drinks'] :
    print(cockid)
  if keyword == i['idDrink'] :
    return keyword
  return render_template("review.html",word=keyword,result=cockid['drinks'], nickname=user_info["nick"])


@app.route('/register/check_dup', methods=['POST'])
def check_dup():
    id_receive = request.form['id_give']
    exists = bool(db.user.find_one({"id": id_receive}))
    # print(value_receive, type_receive, exists)
    return jsonify({'result': 'success', 'exists': exists})


@app.route('/register/check_dup1', methods=['POST'])
def check_dup1():
    nick_receive = request.form['nick_give']
    exists = bool(db.user.find_one({"nick": nick_receive}))
    # print(value_receive, type_receive, exists)
    return jsonify({'result': 'success', 'exists': exists})

@app.route('/user/check_dup2', methods=['POST'])
def check_dup2():
    nick_receive = request.form['nick_give']
    exists = bool(db.user.find_one({"nick": nick_receive}))
    # print(value_receive, type_receive, exists)
    return jsonify({'result': 'success', 'exists': exists})

@app.route('/user/<nikname>')
def user(nick):
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        status = (nick == payload["id"])  # 내 프로필이면 True, 다른 사람 프로필 페이지면 False

        user_info = db.user.find_one({"nick": nick}, {"_id": False})
        return render_template('user.html', user_info=user_info, status=status)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

    