from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class ToDo(db.Model):
    id = db.Column(db.Integer, primary_key=-True)
    title = db.Column(db.String(200), nullable=False)
    complete = db.Column(db.Boolean, nullable=False, default=False)
