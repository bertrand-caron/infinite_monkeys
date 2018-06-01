from os import environ
from typing import Dict, Any, Set
from traceback import format_exc, print_exc
from operator import itemgetter
from json import loads
from flask import Flask, jsonify, request, current_app
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from factory import create_app
from models import db, User, Article, Article_Pair
from similarity import get_word_frequency, article_similarity
from authentification import No_User, User_Not_Admin, Unauthorised_Access, Missing_API_Key, get_user_from_api_key

app = create_app()
try:
    app.config['SQLALCHEMY_DATABASE_URI'] = environ['FLASK_DB']
except KeyError:
    raise Exception('''Please export the FLASK_DB variable in your shell environment. Example: 'export FLASK_DB="mysql://username:password@localhost/db_name"'.''')
app.config['SQLALCHEMY_ECHO'] = True
db.init_app(app)
migrate = Migrate(app, db)

@app.route('/articles', methods=['GET'])
def get_all_articles():
    return jsonify(
        [
            article.as_dict()
            for article in Article.query.all()
        ]
    )

@app.route('/articles/add', methods=['POST'])
def add_article():
    try:
        payload = request.get_json(force=True)
        new_article = Article(**payload)
        db.session.add(new_article)
        db.session.commit()
        return jsonify({'status': 'success', 'new_article': new_article.as_dict()})
    except:
        return (
            jsonify({
                'msg': 'Error adding new Article',
                'status': 'error',
                'traceback': format_exc(),
            }),
            404,
        )

@app.route('/articles/<int:article_id>/delete', methods=['DELETE'])
def delete_article(article_id: int):
    try:
        user = get_user_from_api_key(need_admin=True)
    except Missing_API_Key:
        return jsonify('Missing API key (?api_key=...)'), 404
    except Unauthorised_Access:
        return jsonify('Unauthorised access.'), 404

    db.session.delete(Article.query.filter(Article.id == article_id).one())
    db.session.commit()

    return jsonify(False)

@app.route('/articles/<int:article_id>', methods=['GET'])
def get_url_dict(article_id: int):
    return jsonify(Article.query.filter(Article.id == article_id).one().as_dict())

@app.route('/articles/<int:article_id>/pairs', methods=['GET'])
def get_pairs_for_url(article_id: int):
    return jsonify(
        [
            article_pair.as_dict()
            for article_pair in
            Article_Pair.query.filter(
                (Article_Pair.article_id == article_id) | (Article_Pair._article_id == article_id),
            ).all()
        ],
    )

@app.route('/article_pairs', methods=['GET'])
def get_all_article_pairs():
    FILTERS = {
        'min_score': lambda parameter: Article_Pair.score >= parameter,
        'max_score': lambda parameter: Article_Pair.score <= parameter,
        'article_id': lambda parameter: Article_Pair.article_id == parameter or Article_Pair._article_id == parameter,
    }

    query = Article_Pair.query.join(Article.id)

    for (parameter_name, query_function) in FILTERS.items():
        if parameter_name in request.values:
            query = query.filter(query_function(request.values[parameter_name]))

    return jsonify(
        [
            article_pair.as_dict()
            for article_pair in query.all()
        ]
    )

@app.route('/article_pairs/add', methods=['POST'])
def add_pair():
    payload = request.get_json(force=True)

    def retrieve_or_create_url(url_str: str, text_str) -> Article:
        maybe_url = Article.query.filter(Article.url == url_str).one_or_none()
        if maybe_url is not None:
            return maybe_url
        else:
            user = get_user_from_api_key()
            maybe_url = Article(url=url_str, text=text_str, user_id=user.id)
            db.session.add(maybe_url)
            db.session.flush()
            return maybe_url

    try:
        articles = [
            retrieve_or_create_url(url_str, text_str)
            for (url_str, text_str) in [itemgetter(prefix + 'url', prefix + 'text')(payload) for prefix in ('', '_')]
        ]
    except No_User:
        return jsonify('Unauthorised access.'), 404

    new_article_pair = Article_Pair(
        **dict(zip(
            ('article_id', '_article_id'),
            sorted([article.id for article in articles]),
        )),
        score=article_similarity(
            *map(lambda article: get_word_frequency(article.text), articles)
        ),
    )

    try:
        db.session.add(new_article_pair)
        db.session.commit()
    except IntegrityError:
        return jsonify({'status': 'error', 'details': 'This pair already exists.'}), 404

    return jsonify({'status': 'success', 'new_article_pair': new_article_pair.as_dict()})

@app.route('/users', methods=['GET'])
def get_users():
    try:
        user = get_user_from_api_key(need_admin=True)
    except Unauthorised_Access:
        print_exc()
        return jsonify('Unauthorised access', 404)

    return jsonify(
        [
            user.as_dict()
            for user in User.query.all()
        ]
    )
