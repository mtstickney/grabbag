from link_save.models import APIToken
from link_save.settings import MASTER_API_TOKEN

from datetime import datetime, timedelta
import uuid
import itertools

class InvalidTokenException(Exception):
    def __init__(self, token, reasons):
        self.message = "The token {} is invalid: {}.".format(token, ';'.join(reasons))
        self.token_id = token

class DBTokenRepo:
    # By default, tokens are valid for 24 hours.
    def __init__(self, expiration_length=86400):
        self.expiration_length = timedelta(seconds=expiration_length)

    def _master_token(self):
        return APIToken(token_id=MASTER_API_TOKEN, expiration=None, user=None)

    def clear_expired(self):
        APIToken.objects.filter(expiration__lte=datetime.now()).delete()

    def get_token(self, token):
        if token == MASTER_API_TOKEN:
            return self._master_token()

        try:
            api_token = APIToken.objects.get(token_id=token)
        except APIToken.DoesNotExist:
            raise InvalidTokenException(token, ["there is no such token"])

        if api_token.expiration < datetime.now():
            raise InvalidTokenException(token, ["token is expired"])

        return api_token

    def create_token(self, user):
        token = APIToken(
            token_id=str(uuid.uuid4()),
            expiration=datetime.now() + self.expiration_time,
            user=user
        )
        token.save()
        return token

    def get_all_tokens(self):
        return itertools.chain([self._master_token()], APIToken.objects.all())

class APIAuthorizer:
    def __init__(self, token_repo, user_api_factory, global_api_factory):
        self.token_repo = token_repo
        self.user_api_factory = user_api_factory
        self.global_api_factory = global_api_factory

    def get_api(self, token_id):
        token = self.token_repo.get_token(token_id)
        if token.user is not None:
            return self.user_api_factory(token.user)
        else:
            return self.global_api_factory()
