from typing import Dict, Any
from traceback import format_exc
from operator import itemgetter
from json import loads
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from similarity import get_word_frequency, article_similarity
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
db.create_all()
db.session.commit()
migrate = Migrate(app, db)

class Article(db.Model):
    __tablename__ = 'articles'

    id = db.Column(db.Integer(), primary_key=True)
    url = db.Column(db.String(250), nullable=False)
    text = db.Column(db.Text(), nullable=False)

    #pairs = db.relationship()

    def as_dict(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self) -> str:
        return str(self.__dict__)

class Article_Pair(db.Model):
    __tablename__ = 'article_pairs'

    article_id = db.Column(db.Integer(), db.ForeignKey('articles.id'), nullable=False)
    _article_id = db.Column(db.Integer(), db.ForeignKey('articles.id'), nullable=False)
    score = db.Column(db.Float(), nullable=False)

    __table_args__ = (
        db.PrimaryKeyConstraint('article_id', '_article_id'),
        {},
    )

    def as_dict(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self) -> str:
        return str(self.__dict__)

@app.route('/articles', methods=['GET'])
def get_all_articles():
    return jsonify(
        [
            article.as_dict()
            for article in Article.query.all()
        ]
    )

@app.route('/articles/add', methods=['POST'])
def add_url():
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
            maybe_url = Article(url=url_str, text=text_str)
            db.session.add(maybe_url)
            db.session.flush()
            return maybe_url

    articles = [
        retrieve_or_create_url(url_str, text_str)
        for (url_str, text_str) in [itemgetter(prefix + 'url', prefix + 'text')(payload) for prefix in ('', '_')]
    ]

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
