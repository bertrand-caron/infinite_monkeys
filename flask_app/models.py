from typing import Dict, Any
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(250), unique=True, nullable=False)
    api_key = db.Column(db.String(65), nullable=False)
    is_admin = db.Column(db.Boolean(), default=False)

    def as_dict(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self) -> str:
        return str(self.__dict__)

class Article(db.Model):
    __tablename__ = 'articles'

    id = db.Column(db.Integer(), primary_key=True)
    url = db.Column(db.String(250), nullable=False)
    text = db.Column(db.Text(), nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'), nullable=False)

    user = db.relationship('User')

    def as_dict(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self) -> str:
        return str(self.__dict__)

class Article_Pair(db.Model):
    __tablename__ = 'article_pairs'

    article_id = db.Column(db.Integer(), db.ForeignKey('articles.id'), nullable=False)
    _article_id = db.Column(db.Integer(), db.ForeignKey('articles.id'), nullable=False)
    score = db.Column(db.Float(), nullable=False)

    article = db.relationship('Article', foreign_keys=article_id)
    _article = db.relationship('Article', foreign_keys=_article_id)

    __table_args__ = (
        db.PrimaryKeyConstraint('article_id', '_article_id'),
        {},
    )

    def as_dict(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self) -> str:
        return str(self.__dict__)
