# TODO: these all need tests.

class InvalidUserException(Exception):
    pass

class GlobalApi:
    def __init__(self, token_repo, user_repo):
        self.token_repo = token_repo
        self.user_repo = user_repo

    def create_user_token(self, user):
        if user is None:
            raise InvalidUserException("User for user token must be non-null.")
        token = self.token_repo.create_token(user)
        return token.token_id

    def create_admin_token(self):
        token = self.token_repo.create_token(None)
        return token.token_id

    def create_user(self, username, email, password):
        user = self.user_repo.create_user(username, email, password)
        return user.id

    def delete_user(self, id):
        self.user_repo.delete_by_id(id)

class UserApi:
    def __init__(self, user):
        if user is None:
            raise InvalidUserException("User for user API must be non-null")
        self.__user = user

    def get_user(self):
        # TODO: This really ought to be defensively copied, but
        # Django's ORM doesn't have native support for that. Rats.
        return self.__user
