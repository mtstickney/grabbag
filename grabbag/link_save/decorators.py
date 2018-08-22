from django.http import HttpResponse
from link_save.api_auth import APIAuthorizer, InvalidTokenException

import re

def make_authorizer():
    return APIAuthorizer

class ApiEndpoint:
    def __init__(self, view, auth_factory=APIAuthorizer):
        self.authorizer = auth_factory()
        self.view = view

    def _auth_err_response(self, msg):
        response = HttpResponse(msg, content_type='text/plain;charset=utf-8', status=401)
        response['WWW-Authenticate'] = 'Bearer'
        return response

    def __call__(self, request):
        if 'HTTP_AUTHORIZATION' not in request.META:
            return self._auth_err_response("You must supply an authorization token.")

        match = re.match(r'^(?i)Bearer +([^ ]+)$', request.META['HTTP_AUTHORIZATION'])
        if not match:
            return self._auth_err_response("Malformed Authorization header.")

        try:
            api = self.authorizer.get_api(match.group(1))
        except InvalidTokenException as e:
            return self._auth_err_response("Bad auth token {}: {}".format(e.token_id, e.message))

        request.api = api
        return self.view(request)
