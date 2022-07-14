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
# 몽고디비 주소이며 데이터는 에 저장된다
SECRET_KEY = 'ASD'
# 암호화 할때 사용되는 재료(코드가 정해져있지않음)

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
 # 토큰의 정보를 인증하고 있으며 요청이 들어왓을때 토큰이 삭제되며 메세지를 띄우고 로그인 페이지로 보낸다
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
# 로그인 페이지로 보내는것을 받는다

@app.route('/register')
def register():
    return render_template('register.html')
# 회원가입 페이지로 보내달라는것을 해당위치로 보낸다

@app.route('/api/register', methods=['POST'])
def api_register():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    nickname_receive = request.form['nickname_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    db.user.insert_one({'id': id_receive, 'pw': pw_hash, 'nick': nickname_receive})

    return jsonify({'result': 'success'})
# 저장해달라고 하는 정보를 해당 키워드로 저장하고 패스워드는 암호화 하여 데이터에 아이디와 닉네임과 암호화된 비밀번호 정보를 저장한다

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
# 아이디와 비밀번호가 맞는지 요청해 온것을 비밀번호를 암호화하여 데이터베이스에 아이디와 암호화된 비밀번호가 일치하는지 확인후
# 토큰을 생성하며 토큰의 사용 가능시간은 지금부터 해당시간까지이며 토큰으로서 요청받는것은 접근 권한을 승인 받는다
# 아이디와 암호화된 비밀번호가 일치하지 않을 경우 메세지를 뛰우고 접근권한을 승인하지 않는다

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
 # 아이디에 걸린제한을 통과하는지 확인

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

@app.route('/user/<nick>')
def user(nick):
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        status = (nick == payload["id"])  # 내 프로필이면 True, 다른 사람 프로필 페이지면 False

        user_info = db.user.find_one({"nick": nick}, {"_id": False})
        return render_template('user.html', user_info=user_info, status=status)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))
# 아직 제작 완료하지않음 제작 예정

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

    