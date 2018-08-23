from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods, require_safe
from django.conf import settings
from .decorators import ApiEndpoint
from .api_auth import DBTokenRepo, APIAuthorizer
from .api import UserApi, GlobalApi
from .users import DBUserRepo, UserExistsException
from .models import User

import json

def make_default_auth():
    token_repo = DBTokenRepo()
    return APIAuthorizer(token_repo, )

def make_default_app():
    user_repo = DBUserRepo()
    token_repo = DBTokenRepo()
    return LinkSaveV1ApiApp(token_repo, user_repo)

# Adapter to use ApiEndpoint on methods, and to plug in the API app as
# the factory for api objects. Has an unfortunate performance impact,
# because it reconstructs the wrapped method on each call :(
def endpoint(method):
    def Adapter(self, request, **kwargs):
        view = ApiEndpoint(
            lambda request: method(self, request, **kwargs),
            auth_factory=self.make_authorizer
        )
        return view(request)
    return Adapter

# TODO: each ApiEndpoint decorator is creating its own authorizer
# instance, which we really don't need. Use a shared instance instead.

class LinkSaveV1ApiApp:
    def __init__(self, token_repo, user_repo):
        self.user_repo = user_repo
        self.token_repo = token_repo
        self.api_auth = APIAuthorizer(self.token_repo, self.make_user_api, self.make_global_api)

    def make_user_api(self, user):
        return UserApi(user)

    def make_global_api(self):
        return GlobalApi(self.token_repo, self.user_repo)

    def make_authorizer(self):
        return self.api_auth

    @endpoint
    def get_tokens(self, request):
        tokens = [t.token_id for t in self.token_repo.get_all_tokens()]
        return JsonResponse(tokens, safe=False)

    @endpoint
    def create_admin_token(self, request):
        if not isinstance(request.api, GlobalApi):
            raise UnauthorizedException("You are not authorized to administrator tokens.")

        token = request.api.create_admin_token()
        return JsonResponse(token)

    @endpoint
    def get_users(self, request, id=None):
        if not isinstance(request.api, GlobalApi):
            raise UnauthorizedException("You are not authorized to list users.")

        if id is not None:
            if request.method == 'DELETE':
                return self.delete_user(request, id=id)

            try:
                user = self.user_repo.get_user_by_id(id)
                return JsonResponse({"id": user.id, "username": user.username, "email": user.email, "password": None})
            except User.DoesNotExist:
                return HttpResponse("No such user.", content_type='text/plain;charset=utf-8', status=404)
        else:
            users = [{
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "password": None
            } for u in self.user_repo.get_all_users()]

            return JsonResponse(users, safe=False)

    # You might think PUT would be the trendy thing to support here,
    # but we're not allowing users to specify user IDs on creation, so
    # it's actually not appropriate.
    @endpoint
    def create_user(self, request):
        if not isinstance(request.api, GlobalApi):
            raise UnauthorizedException("You are not authorized to create users.")

        if request.content_type  != 'application/json':
            return HttpResponse("Invalid content-type.", status=400)

        data = json.loads(request.body.decode(request.encoding if request.encoding is not None else settings.DEFAULT_CHARSET))
        if 'username' not in data or not isinstance(data['username'], str):
            return HttpResponse("Invalid username.", status=400)
        if 'email' not in data or (data['email'] is not None and not isinstance(data['email'], str)):
            return HttpResponse("Invalid email.", status=400)
        if 'password' not in data or not isinstance(data['password'], str):
            return HttpResponse("Invalid password.", status=400)

        try:
            user = request.api.create_user(data['username'], data['password'], data['email'])
        except UserExistsException as e:
            return HttpResponse("A user with username {} already exists.".format(data['username']), status=409)

        return JsonResponse(user)

    @endpoint
    def delete_user(self, request, id):
        if not isinstance(request.api, GlobalApi):
            raise UnauthorizedException("You are not authorized to delete users.")

        if request.content_type != 'application/json':
            return HttpResponse("Invalid content-type.", status=400)

        try:
            request.api.delete_user(id)
        except User.DoesNotExist:
            return HttpResponse("There is no such user.", status=404)

        return HttpResponse('')
