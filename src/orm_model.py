from flask_sqlalchemy import SQLAlchemy


DB = SQLAlchemy()


class Author(DB.Model):
    """A table (Author) containing an identifier (id) and username (name)"""
    id = DB.Column(DB.BigInteger, primary_key=True, nullable=False)
    name = DB.Column(DB.String, nullable=False)


class Tweet(DB.Model):

    id = DB.Column(DB.BigInteger, primary_key=True, nullable=False)
    body = DB.Column(DB.Unicode(300))
    author_id = DB.Column(DB.BigInteger, DB.ForeignKey('author.id'), nullable=False)
    author = DB.relationship('Author', backref=DB.backref('tweets', lazy=True))
