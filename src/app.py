import os

import flask
from flask import Flask, request, render_template
import spacy
from sqlalchemy.exc import IntegrityError
import tweepy

from src.orm_model import DB, Author
from src.twitter import upsert_user
from src.twitter_assist import upsert_author_assist


def create_app() -> flask.app.Flask:
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/twitter_db.sqlite3'
    DB.init_app(app)

    @app.route('/')
    def landing():
        return render_template('landing.html', authors=Author.query.order_by(Author.id))  # Author.query.all()

    @app.route('/add_author')
    def add_author():
        author_handle = request.args['author_handle']
        twitter_auth = tweepy.OAuthHandler(os.environ['TWITTER_API_KEY'], os.environ['TWITTER_API_KEY_SECRET'])
        twitter_api = tweepy.API(twitter_auth)
        spacy_path = 'src/my_model'
        spacy_model = spacy.load(spacy_path)
        upsert_user(author_handle=author_handle, twitter_api=twitter_api, spacy_model=spacy_model)
        try:
            return render_template('landing.html', authors=Author.query.order_by(Author.id))
        except IntegrityError as e:
            return f'Id is already in database.<br>{str(e)}'

    @app.route('/add_author_assist')
    def add_author_assist():
        author_handle = request.args['author_handle']
        spacy_path = 'src/my_model'
        spacy_model = spacy.load(spacy_path)
        upsert_author_assist(author_handle=author_handle, spacy_model=spacy_model)
        try:
            return render_template('landing.html', authors=Author.query.order_by(Author.id))
        except IntegrityError as e:
            return f'Id is already in database.<br>{str(e)}'

    @app.route('/classify_post')
    def classify_post():
        most_likely_author = request.args['post_text'][-5:]
        return most_likely_author

    @app.route('/reset')
    def reset_db():
        DB.drop_all()
        DB.create_all()
        return 'Database reset!'

    return app


if __name__ == '__main__':
    # create_app().run(host='0.0.0.0')
    create_app().run()
