from flask import Flask, request, render_template
from sqlalchemy.exc import IntegrityError

from src.orm_model import DB, Author


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/twitter_db.sqlite3'
    DB.init_app(app)

    @app.route('/')
    def landing():
        return render_template('landing.html', authors=Author.query.order_by(Author.id))  # Author.query.all()

    @app.route('/add_author')
    def add_author():
        id = request.args['id']
        name = request.args['name']
        new_author = Author(id=id, name=name)
        try:
            DB.session.add(new_author)
            DB.session.commit()
            return ', '.join([k.name for k in Author.query.all()])
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
    create_app().run()
