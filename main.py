from flask import Flask, render_template, redirect, request, url_for, flash
from flask_bootstrap import Bootstrap
from werkzeug.security import check_password_hash, generate_password_hash
from forms import TodoList, Tasks, Login, Signup
from flask_login import LoginManager, login_required, login_user, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'success'
app.config['SECRET_KEY'] = '0c97eda389c9b70d187b7879e7993ebbc6b9b68e'


# DB Models
@login_manager.user_loader
def load_user(id):
    return User.query.get(id)


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(10), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    groups = db.relationship('TodoGroup', backref='todo_lists', lazy=True)

    def __repr__(self):
        return f"User({self.username})"


class TodoGroup(db.Model):
    __tablename__ = 'todogroups'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(15), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    task = db.relationship('Task', backref='list_tasks', lazy=True, cascade="all,delete-orphan")

    def __repr__(self):
        return f"User({self.title})"


class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    task_title = db.Column(db.String(15), nullable=False, unique=True)
    due_date = db.Column(db.DateTime, nullable=False)
    due_time = db.Column(db.Time, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    todo_id = db.Column(db.Integer, db.ForeignKey('todogroups.id'), nullable=False)

    def __repr__(self):
        return f"User({self.task_title}, {self.due_date}, {self.due_time})"


@app.route('/')
def home():
    if current_user.is_authenticated:
        todos = TodoGroup.query.filter_by(user_id=current_user.id).order_by(TodoGroup.date_added.desc()).all()
        if todos:
            most_recent = todos[0]
            older = todos[1:]
            return render_template('index.html', todos=older, recent=most_recent)
    return render_template('index.html')


@app.route('/login', methods=["POST", "GET"])
def login():
    form = Login()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                next_page = request.args.get('next')
                flash('Logged in!', 'success')
                return redirect(next_page) if next_page else redirect(url_for('home'))
            else:
                flash('Wrong password', 'danger')
        else:
            flash(f'{form.username.data} does not exist.', 'danger')
    return render_template('login.html', form=form)


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    form = Signup()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(
            username=form.username.data,
            password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        flash("Signed Up!", "success")
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)


@app.route('/add-list', methods=['POST', 'GET'])
@login_required
def add_list():
    form = TodoList()
    if form.validate_on_submit():
        todo = TodoGroup(
            title=form.list_name.data,
            description=form.list_description.data,
            user_id=current_user.id
        )
        db.session.add(todo)
        db.session.commit()
        flash('Todo List added', 'success')
        return redirect(url_for('home'))
    return render_template('add_list.html', form=form)


@app.route('/tasks/<int:todo_id>', methods=['POST', 'GET'])
@login_required
def add_task(todo_id):
    form = Tasks()
    if form.validate_on_submit():
        task = Task(
            task_title=form.task_name.data,
            due_date=form.due_date.data,
            due_time=form.due_time.data,
            todo_id=todo_id
        )
        db.session.add(task)
        db.session.commit()
        flash("Task added", 'success')
        return redirect(url_for('view_todo', todo_id=todo_id))
    return render_template('add_list.html', form=form)


@app.route('/view-todo/<int:todo_id>')
@login_required
def view_todo(todo_id):
    tasks = Task.query.filter_by(todo_id=todo_id).order_by(Task.due_date.asc(), Task.due_time.asc()).all()
    return render_template('to_do.html', tasks=tasks, todo_id=todo_id)


@app.route('/complete/<int:task_id>')
@login_required
def complete_task(task_id):
    task = Task.query.get(task_id)
    task.completed = True
    db.session.commit()
    return redirect(url_for('view_todo', todo_id=task.todo_id))


@app.route('/reinstate/<int:task_id>')
def reinstate(task_id):
    task = Task.query.get(task_id)
    task.completed = False
    db.session.commit()
    return redirect(url_for('view_todo', todo_id=task.todo_id))


@app.route('/delete_list/<int:list_id>')
@login_required
def delete_list(list_id):
    todo_list = TodoGroup.query.get(list_id)
    db.session.delete(todo_list)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/delete_task/<int:task_id>')
@login_required
def delete_task(task_id):
    task = Task.query.get(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('view_todo', todo_id=task.todo_id))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
