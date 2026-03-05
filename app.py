from __future__ import annotations
from flask import Flask, render_template, redirect, request, flash
from flask_scss import Scss
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column

# App
app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for flash messages

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db = SQLAlchemy(app)

# Data class
class MyTask(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(db.String(100), nullable=False)
    complete: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=db.func.now())

    def __repr__(self) -> str:
        return f"<Task {self.id}>"

# Index route
@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        current_task = request.form['content']
        new_task = MyTask(content=current_task)
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect("/")
        except Exception as e:
            print(f"err:{e}")
            return f"err:{e}"
    else:
        tasks = MyTask.query.order_by(MyTask.created_at).all()
        return render_template('index.html', tasks=tasks)

# Deleting
@app.route("/delete/<int:id>")
def delete(id: int):
    delete_task = MyTask.query.get_or_404(id)
    try:
        db.session.delete(delete_task)
        db.session.commit()
        flash("Task deleted successfully!", "success")
        return redirect("/")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting task: {e}", "danger")
        return redirect("/")

# Editing
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id: int):
    task = MyTask.query.get_or_404(id)
    if request.method == "POST":
        task.content = request.form["content"]
        try:
            db.session.commit()
            flash("Task updated successfully!", "success")
            return redirect("/")
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating task: {e}", "danger")
            return redirect("/")
    else:
        return render_template("edit.html", task=task)

# Run app (must be last!)
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
