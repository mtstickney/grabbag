from link_save.models import APIToken
from link_save.settings import MASTER_API_TOKEN
from link_save.api import GlobalApi, UserApi

from datetime import datetime, timedelta
import uuid

class InvalidTokenException(Exception):
    def __init__(self, token, reasons):
        self.message = "The token {} is invalid: {}.".format(token, ';'.join(reasons))
        self.token = token

class DBTokenRepo:
    # By default, tokens are valid for 24 hours.
    def __init__(self, expiration_length=86400):
        self.expiration_length = timedelta(seconds=expiration_length)

    def clear_expired(self):
        APIToken.objects.filter(expiration__lte=datetime.now()).delete()

    def get_token(self, token):
        if token == MASTER_API_TOKEN:
            return APIToken(token_id=MASTER_API_TOKEN, expiration=None, user=None)

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

class APIAuthenticator:
    def __init__(self, token_repo):
        self.token_repo = token_repo

    def get_api(self, token_id):
        token = self.token_repo.get_token(token_id)
        if token.user is not None:
            return UserApi(token.user)
        else:
            return GlobalApi(self.token_repo)
