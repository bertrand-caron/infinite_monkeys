import begin

from application import db, User, Article

@begin.subcommand
def init_db() -> None:
    db.create_all()

    if len(User.query.all()) == 0:
        db.session.add(User(email='admin@local.host', api_key='123', is_admin=True))

    if len(Article.query.all()) == 0:
        db.session.add(Article(url='abc.net/news', text='This is news! Watch out!', user_id=1))

    db.session.commit()

@begin.subcommand
def reset_db() -> None:
    db.drop_all()
    init_db()

@begin.start
def run():
    pass
