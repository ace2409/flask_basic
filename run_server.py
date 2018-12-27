from flask import Flask, render_template, url_for, request, session, redirect, send_from_directory, jsonify
from flask_pymongo import PyMongo
import bcrypt

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'ques'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/ques'

mongo = PyMongo(app)

app.secret_key = 'mysecret'

@app.route('/')
def ind():
    if 'username' in session:
        return 'hi'
    else:
        return redirect('/userlogin')

@app.route('/view_question/<id>')
def index(id):
    questions = mongo.db.questions
    all_questions = questions.find_one({'id' : id})
    question = all_questions['question']
    option1 = all_questions['a']
    option2 = all_questions['b']
    next_id = int(id) + 1
    return render_template('index.html', question=question, option1=option1, option2=option2, next_id=next_id)

# Login and register 
@app.route('/register', methods=['POST', 'GET'])
def register():
    if 'username' in session:
        return redirect('/')
    if request.method == 'POST':
        users = mongo.db.users
        user_fname = request.form.get('name')
        # user_fname = request.form['name']
        user_email = request.form.get('email')
        existing_user = users.find_one({'name': request.form.get('username')})
        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form.get('password').encode('utf-8'), bcrypt.gensalt())
            users.insert(
                {'fullname': user_fname, 'email': user_email, 'name': request.form.get('username'),
                 'user_type': 'worker', 'password': hashpass})
            session['username'] = request.form.get('username')
            return redirect('/')

        return 'A user with that Email id/username already exists'

    return render_template('signup.html')

@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'name': request.form['username']})

    if login_user:
        if bcrypt.hashpw(request.form.get('password').encode('utf-8'), login_user['password']) == login_user[
            'password']:
            session['username'] = request.form['username']
            return redirect('/')

    return 'Invalid username/password combination'

@app.route('/userlogin', methods=['POST', 'GET'])
def userlogin():
    if 'username' in session:
        return redirect('/')

    return render_template('signin.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')


if __name__ == "__main__":
    app.run(host='0.0.0.0')
