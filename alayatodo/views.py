from flask import (
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for
    )

from alayatodo import app
from alayatodo.model import Todo, TodoDescriptionError, User


@app.route('/')
def home():
    with app.open_resource('../README.md', mode='r') as f:
        readme = "".join(l.decode('utf-8') for l in f)
        return render_template('index.html', readme=readme)


@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_POST():
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.authenticate(username, password)
    if user:
        session['user'] = user
        session['logged_in'] = True
        return redirect(url_for('todos'))

    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    return redirect(url_for('home'))


@app.route('/todo/<id>', methods=['GET'])
def todo(id):
    todo = Todo.get(id)
    return render_template('todo.html', todo=todo)


@app.route('/todo', methods=['GET'])
@app.route('/todo/', methods=['GET'])
def todos():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    todos = Todo.all()
    return render_template('todos.html', todos=todos)


@app.route('/todo', methods=['POST'])
@app.route('/todo/', methods=['POST'])
def todos_POST():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    try:
        Todo.new(session['user']['id'], request.form.get('description', ''))
    except TodoDescriptionError:
        flash('Todo requires additional content', 'danger')
        return redirect(url_for('todos'))
    return redirect(url_for('todos'))


@app.route('/todo/<id>', methods=['POST'])
def todo_delete(id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    Todo.delete(id)
    return redirect(url_for('todos'))
