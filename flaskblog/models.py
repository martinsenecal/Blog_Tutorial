# Use Class-Model for db
from datetime import datetime
from flaskblog import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)  # Each Username is Unique and we need one.
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')  # Hash Image
    password = db.Column(db.String(60), nullable=False)  # Hash Password
    posts = db.relationship('Post', backref='author', lazy=True)  # One user can have many posts.

    def __repr__(self):
        return f"User('{self.username}','{self.email}','{self.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}','{self.date_posted}')"

