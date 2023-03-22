from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, SubmitField, TextAreaField, validators
from datetime import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = 'jhsbdKJ34unkj9238nfqel'
Bootstrap(app)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Table Configuration
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    complete = db.Column(db.Integer, nullable=False)
    item = db.Column(db.String(250), nullable=False)
    due_date = db.Column(db.String, nullable=True)
    priority = db.Column(db.String, nullable=True)
    tag_color = db.Column(db.String, nullable=True)
    note = db.Column(db.String, nullable=True)


# Task form
class TaskForm(FlaskForm):
    item = StringField('Task', validators=[validators.input_required()])
    due_date = DateField('Due Date', validators=[validators.optional()])
    priority = SelectField("Priority", choices=(" ", "Low", "Medium", "High"), validators=[validators.optional()])
    tag_color = SelectField("Tag Color", choices=(" ", "Red", "Orange", "Yellow", "Green", "Blue", "Purple"), validators=[validators.optional()])
    note = TextAreaField("Notes", validators=[validators.optional()])
    submit = SubmitField('Submit')


# Task update form
class TaskUForm(FlaskForm):
    item = StringField('Task', validators=[validators.input_required()])
    due_date = DateField('Due Date', validators=[validators.optional()])
    priority = SelectField("Priority", choices=(" ", "Low", "Medium", "High"), validators=[validators.optional()])
    tag_color = SelectField("Tag Color", choices=(" ", "Red", "Orange", "Yellow", "Green", "Blue", "Purple"), validators=[validators.optional()])
    note = TextAreaField("Notes", validators=[validators.optional()])
    update = SubmitField('Update')


# Used to generate new tables
with app.app_context():
    db.create_all()


# Home page
@app.route("/")
def home():
    all_tasks = Todo.query.all()
    all_tasks_list = []
    for task in all_tasks:
        tinfo = {
            "id": task.id,
            "complete": task.complete,
            "item": task.item,
            "due_date": task.due_date,
            "priority": task.priority,
            "tag_color": task.tag_color,
            "note": task.note
        }
        all_tasks_list.append(tinfo)
    return render_template("index.html", tasks=all_tasks_list)


# Add task page
@app.route("/new-task", methods=["GET", "POST"])
def add_task():
    form = TaskForm()
    if form.validate_on_submit():
        try:
            dd = datetime.strptime(request.form.get("due_date"), "%Y-%m-%d").strftime("%m-%d-%Y")
            new_task = Todo(due_date=dd)
        except ValueError:
            new_task = Todo(due_date=request.form.get("due_date"))
        finally:
            new_task = Todo(
                complete=0,
                item=request.form.get("item"),
                due_date=request.form.get("due_date"),
                priority=request.form.get("priority"),
                tag_color=request.form.get("tag_color"),
                note=request.form.get("note"),
            )
            db.session.add(new_task)
            db.session.commit()
        return redirect(url_for("home"))
    return render_template("add_task.html", form=form)


# See/update task info
@app.route("/task/<task_id>", methods=["GET", "POST"])
def task_info(task_id):
    task = Todo.query.get(task_id)
    form = TaskUForm()
    if form.validate_on_submit():
        try:
            dd = datetime.strptime(request.form.get("due_date"), "%Y-%m-%d").strftime("%m-%d-%Y")
            task.due_date = dd
        except ValueError:
            task.due_date = request.form.get("due_date")
        finally:
            task.item = request.form.get("item")
            task.priority = request.form.get("priority")
            task.tag_color = request.form.get("tag_color")
            task.note = request.form.get("note")
            db.session.commit()
        flash("This task has been updated.")
        return redirect(url_for("task_info", task_id=task.id))
    else:
        try:
            form.due_date.data = datetime.strptime(f"{task.due_date}", "%m-%d-%Y")
        except ValueError:
            form.due_date.data = task.due_date
        finally:
            form.item.data = task.item
            form.priority.data = task.priority
            form.tag_color.data = task.tag_color
            form.note.data = task.note
        return render_template("task_info.html", form=form, task=task)


@app.route("/delete/<task_id>", methods=["GET", "DELETE"])
def delete_task(task_id):
    task = Todo.query.get(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/complete/<task_id>", methods=["GET", "POST"])
def complete_task(task_id):
    task = Todo.query.get(task_id)
    task.complete = 1
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/undo-complete/<task_id>", methods=["GET", "POST"])
def undo_complete(task_id):
    task = Todo.query.get(task_id)
    task.complete = 0
    db.session.commit()
    return redirect(url_for("home"))


# Run the application
if __name__ == '__main__':
    app.run(debug=True)
