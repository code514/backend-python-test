from flask import (
    flash,
    jsonify,
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
    if not user:
        flash('Nope', 'danger')
        return redirect(url_for('login'))

    session['user'] = {
        'id': user['id'],
        'username': user['username']
    }
    return goto_todos()


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))


@app.route('/todo', methods=['GET'])
@app.route('/todo/', methods=['GET'])
def todos():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))

    per_page = app.config['TODOS_PER_PAGE']
    total_pages = (Todo.count(user_id=user['id']) - 1) / per_page + 1
    try:
        current_page = int(request.args['page'])
    except Exception:
        current_page = 1
    if current_page < 0:
        # Negative pages count down from the end, with -1 being the last page
        current_page = total_pages + current_page + 1
        if current_page < 0:
            # Went too far in the negatives
            current_page = 1
    if current_page > total_pages:
        current_page = total_pages

    # Prepare page numbers to show in pagination
    # Show max 5 pages, centered around current page as best we can
    min_page = max(1, current_page - 2)
    max_page = min(total_pages, current_page + (5 - 1 - (current_page - min_page)))
    # Recompute min in case we don't have enough pages on the right side of the current one
    min_page = max(1, current_page - (5 - 1 - (max_page - current_page)))
    pages = [min_page + i for i in range(max_page - min_page + 1)]

    todos = Todo.for_user(user['id'], limit=per_page, offset=(current_page - 1) * per_page)

    return render_template(
        'todos.html',
        todos=todos,
        total_pages=total_pages,
        page=current_page,
        pages=pages
    )


@app.route('/todo', methods=['POST'])
@app.route('/todo/', methods=['POST'])
def todos_POST():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))

    try:
        todo = Todo.new(user['id'], request.form.get('description', ''))
    except TodoDescriptionError:
        return goto_todos(error='Todo requires additional content')
    return goto_todos(success='"{}" created'.format(todo['description']), page=-1)


@app.route('/todo/<id>', methods=['GET'])
def todo(id):
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))

    todo = Todo.get(id)
    if todo is None or todo['user_id'] != user['id']:
        return goto_todos(error='Todo not found')

    return render_template('todo.html', todo=todo)


@app.route('/todo/<id>/json', methods=['GET'])
def todo_json(id):
    user = session.get('user')
    if not user:
        return jsonify({
            'success': False,
            'message': 'Authentication required'
        }), 403

    todo = Todo.get(id)
    if todo is None or todo['user_id'] != user['id']:
        return jsonify({
            'success': False,
            'message': 'Todo not found'
        }), 404

    # Keep resource representations separate from models
    representation = {
        'id': todo['id'],
        'user_id': todo['user_id'],
        'description': todo['description'],
        'completed': todo['completed'] == 1
    }
    return jsonify(representation)


@app.route('/todo/<id>', methods=['POST'])
def todo_POST(id):
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))

    todo = Todo.get(id)
    if todo is None or todo['user_id'] != user['id']:
        return goto_todos(error='Todo not found')

    if request.form.get('description') == '':
        Todo.delete(id)
        return goto_todos(success='"{}" deleted'.format(todo['description']))

    if request.form.get('completed') == '1':
        Todo.complete(id)
        return goto_todos(success='"{}" completed'.format(todo['description']))


def goto_todos(info=None, success=None, error=None, warning=None, **kwargs):
    if info:
        flash(info, 'info')
    if success:
        flash(success, 'success')
    if error:
        flash(error, 'danger')
    if warning:
        flash(warning, 'warning')

    if 'page' not in kwargs:
        kwargs['page'] = request.args.get('page')

    return redirect(url_for('todos', **kwargs))
