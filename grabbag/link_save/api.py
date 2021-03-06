from functools import wraps

from .decorators import UnauthorizedException

# TODO: these all need tests.

class InvalidUserException(Exception):
    pass


def apistub(msg=None):
    def wrapper(method):
        @wraps(method)
        def wrapped(self, *args, **kwargs):
            raise UnauthorizedException(msg if msg is not None else "You are not authorized to perform this operation")
        return wrapped
    return wrapper

class ApiOperations:
    @apistub(msg="You are not authorized to create administrator tokens.")
    def create_admin_token(self): pass

    @apistub(msg="You are not authorized to create user tokens.")
    def create_user_token(self): pass

    @apistub(msg="You are not authorized to list tokens.")
    def get_all_tokens(self): pass

    @apistub(msg="You are not authorized to create users.")
    def create_user(self): pass

    @apistub(msg="You are not authorized to delete users.")
    def delete_user(self): pass

    @apistub(msg="You are not authorized to list users.")
    def get_user(self): pass

    @apistub(msg="You are not authorized to list users.")
    def get_all_users(self): pass

    @apistub(msg="You are not authorized to alter user data.")
    def update_user(self): pass

class GlobalApi(ApiOperations):
    def __init__(self, token_repo, user_repo):
        self.token_repo = token_repo
        self.user_repo = user_repo

    def create_admin_token(self):
        token = self.token_repo.create_token(None)
        return token.token_id

    def create_user_token(self, id):
        user = self.get_user(id)
        token = self.token_repo.create_token(user)
        return token.token_id

    def get_all_tokens(self):
        return self.token_repo.get_all_tokens()

    def create_user(self, username, email, password):
        user = self.user_repo.create_user(username, email, password)
        return user.id

    def delete_user(self, id):
        self.user_repo.delete_by_id(id)

    def get_user(self, id):
        return self.user_repo.get_user_by_id(id)

    def get_all_users(self):
        return  self.user_repo.get_all_users()

    def update_user(self, id, data):
        user = self.get_user(id)
        if 'password' in data:
            user.set_password(data['password'])
        if 'email' in data:
            user.email = data['email']
        if 'username' in data:
            user.username = data['username']
        return self.user_repo.update_user(user)


class UserApi(ApiOperations):
    def __init__(self, user, token_repository):
        if user is None:
            raise InvalidUserException("User for user API must be non-null")
        self.__user = user
        self.token_repository = token_repository

    def get_user(self, id):
        if id != self.__user.id:
            raise UnauthorizedException("You are not authorized to retrieve other users' data.")

        # TODO: This really ought to be defensively copied, but
        # Django's ORM doesn't have native support for that. Rats.
        return self.__user

    def create_user_token(self, id):
        user = self.get_user(id)
        return self.token_repository.create_token(user)

    def update_user(self, id, data):
        user = self.get_user(id)
        if 'password' in data:
            user.set_password(data['password'])
        if 'email' in data:
            user.email = data['email']
        if 'username' in data:
            user.data = data['username']
        return self.user_repo.update_user(user)
