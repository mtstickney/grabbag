from django.test import SimpleTestCase

from link_save.settings import MASTER_API_TOKEN
from link_save.api_auth import APIAuthorizer, InvalidTokenException
from link_save.api import GlobalApi, UserApi
from link_save.models import APIToken, User
from datetime import datetime, timedelta

import uuid

class MemoryTokenRepo:
    def __init__(self, expiration_length=500):
        self.expiration_length = timedelta(seconds=expiration_length)
        self.tokens = {}

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

class TestApiOracle(SimpleTestCase):
    def test_missing_token_denied(self):
        authenticator = APIAuthorizer(MemoryTokenRepo())
        with self.assertRaises(InvalidTokenException):
            authenticator.get_api('abcdef')

    def test_master_token_accepted(self):
        authenticator = APIAuthorizer(MemoryTokenRepo())
        api = authenticator.get_api(MASTER_API_TOKEN)
        self.assertIsInstance(api, GlobalApi)

    def test_expired_token_denied(self):
        authenticator = APIAuthorizer(MemoryTokenRepo(expiration_length=-1))

        # Create a token that will be instantly expired.
        api = authenticator.get_api(MASTER_API_TOKEN)
        token_id = api.create_admin_token()

        with self.assertRaises(InvalidTokenException):
            authenticator.get_api(token_id)

    def test_user_token_accepted(self):
        authenticator = APIAuthorizer(MemoryTokenRepo())
        admin_api = authenticator.get_api(MASTER_API_TOKEN)

        user = User(id=1, username='jimmy')
        token_id = admin_api.create_user_token(user)

        api = authenticator.get_api(token_id)
        self.assertIsInstance(api, UserApi)
        self.assertEqual(api.get_user().id, 1)
