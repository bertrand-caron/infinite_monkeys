import begin

from application import app, db, User, Article, Article_Pair

with app.app_context():
    @begin.subcommand
    def init_db() -> None:
        db.create_all()
        db.session.commit()

        if len(User.query.all()) == 0:
            user = User(email='admin@local.host', api_key='123', is_admin=True)
            db.session.add(user)
            db.session.commit()
        else:
            user = User.query.one()

        if len(Article.query.all()) < 2:
            article_1, article_2 = [
                Article(url='abc.net/news', text='This is news! Watch out!', user_id=user.id),
                Article(url='abc.net/more-news', text='This is more news! Watch out!', user_id=user.id),
            ]
            db.session.bulk_save_objects([article_1, article_2])
            db.session.commit()
        else:
            article_1, article_2 = Article.query.limit(2).all()

        if len(Article_Pair.query.all()) == 0:
            db.session.add(Article_Pair(article_id=min({article_1.id, article_2.id}), _article_id=max({article_1.id, article_2.id}), score=0.5))
            db.session.commit()

    @begin.subcommand
    def reset_db() -> None:
        db.drop_all()
        init_db()

    @begin.start
    def run():
        pass
