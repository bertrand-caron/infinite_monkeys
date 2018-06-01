from flask import request

from models import User

class Unauthorised_Access(RuntimeError):
    pass

class No_User(Unauthorised_Access):
    pass

class User_Not_Admin(Unauthorised_Access):
    pass

class Missing_API_Key(Unauthorised_Access):
    pass

def get_user_from_api_key(need_admin: bool = False) -> User:
    try:
        if 'api_key' not in request.values:
            raise Missing_API_Key
        else:
            user = User.query.filter(User.api_key == request.values['api_key']).one()
            if need_admin and not user.is_admin:
                raise User_Not_Admin
    except NoResultFound:
        raise No_User
