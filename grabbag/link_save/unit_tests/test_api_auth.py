from django.test import SimpleTestCase

from link_save.settings import MASTER_API_TOKEN
from link_save.api_auth import APIAuthorizer, InvalidTokenException
from link_save.api import GlobalApi, UserApi
from link_save.decorators import UnauthorizedException
from link_save.models import APIToken, User
from datetime import datetime, timedelta

import uuid

# CLEANUP: constructing actual API objects is going to get pretty
# hairy as they get more complex, which makes this test suite
# fragile.

class MemoryTokenRepo:
    def __init__(self, expiration_length=500):
        self.expiration_length = timedelta(seconds=expiration_length)
        self.tokens = {}
        self.users = [User(id=1, username="jimmy")]

    def clear_expired(self):
        tokens = self.tokens.keys()
        for t in tokens:
            api_token = self.tokens[t]
            if api_token.expiration < datetime.now():
                del self.tokens[t]

    def get_token(self, token):
        if token == MASTER_API_TOKEN:
            return APIToken(token, expiration=None, user=None)

        if token not in self.tokens:
            raise InvalidTokenException(token, ["token is not valid"])

        api_token = self.tokens[token]
        if api_token.expiration < datetime.now():
            raise InvalidTokenException(token, ["token has expired"])

        return api_token

    def create_token(self, user):
        token_id = str(uuid.uuid4())
        token = APIToken(token_id=token_id, expiration=datetime.now() + self.expiration_length, user=user)
        self.tokens[token_id] = token
        return token

    def make_user_api(self, user):
        return UserApi(user, self)

    def make_global_api(self):
        return GlobalApi(self, self)

    # User repository methods.
    def get_user_by_id(self, id):
        for u in self.users:
            if u.id == id:
                return u
        raise User.DoesNotExist

class StubUserApi(UserApi):
    def __init__(self):
        pass

class StubGlobalApi(GlobalApi):
    def __init__(self):
        pass

def make_test_authorizer(expiration=86400):
    token_repo = MemoryTokenRepo(expiration_length=expiration)
    return APIAuthorizer(token_repo, token_repo.make_user_api, token_repo.make_global_api)

class TestApiOracle(SimpleTestCase):
    def test_missing_token_denied(self):
        authenticator = make_test_authorizer()
        with self.assertRaises(InvalidTokenException):
            authenticator.get_api('abcdef')

    def test_master_token_accepted(self):
        authenticator = make_test_authorizer()
        api = authenticator.get_api(MASTER_API_TOKEN)
        self.assertIsInstance(api, GlobalApi)

    def test_expired_token_denied(self):
        authenticator = make_test_authorizer(-1)

        # Create a token that will be instantly expired.
        api = authenticator.get_api(MASTER_API_TOKEN)
        token_id = api.create_admin_token()

        with self.assertRaises(InvalidTokenException):
            authenticator.get_api(token_id)

    def test_user_token_accepted(self):
        authenticator = make_test_authorizer()
        admin_api = authenticator.get_api(MASTER_API_TOKEN)

        user_id = 1
        token_id = admin_api.create_user_token(user_id)

        api = authenticator.get_api(token_id)
        self.assertIsInstance(api, UserApi)
        with self.assertRaises(UnauthorizedException):
            api.get_user(2)
        self.assertEqual(api.get_user(user_id).id, 1)

    def test_undefined_op_attributeerror(self):
        admin_api = StubGlobalApi()
        user_api = StubUserApi()

        # Normal invalid method calls result in an AttributeError.
        with self.assertRaises(AttributeError):
            admin_api.not_a_method()

        with self.assertRaises(AttributeError):
            user_api.not_a_method()

    def test_unimplemented_op_unauthorized_error(self):
        user_api = StubUserApi()
        # unimplemented methods defined as API operatrions raise an UnauthorizedException
        with self.assertRaises(UnauthorizedException):
            user_api.create_admin_token()
