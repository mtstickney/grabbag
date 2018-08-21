class InvalidUserException(Exception):
    pass

class GlobalApi:
    def __init__(self, token_repo):
        self.token_repo = token_repo

    def create_user_token(self, user):
        if user is None:
            raise InvalidUserException("User for user token must be non-null.")
        token = self.token_repo.create_token(user)
        return token.token_id

    def create_admin_token(self):
        token = self.token_repo.create_token(None)
        return token.token_id

class UserApi:
    def __init__(self, user):
        if user is None:
            raise InvalidUserException("User for user API must be non-null")
        self.__user = user

    def get_user(self):
        # TODO: This really ought to be defensively copied, but
        # Django's ORM doesn't have native support for that. Rats.
        return self.__user
