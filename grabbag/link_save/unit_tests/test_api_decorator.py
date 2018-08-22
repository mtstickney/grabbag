from django.test import SimpleTestCase
from django.http import HttpRequest, HttpResponse, Http404
from link_save.decorators import ApiEndpoint
from link_save.settings import MASTER_API_TOKEN
from link_save.api import GlobalApi, UserApi
from link_save.api_auth import InvalidTokenException

class StubUserApi(UserApi):
    def __init__(self):
        pass

class StubGlobalApi(GlobalApi):
    def __init__(self):
        pass

class MockAuthorizer:
    def get_api(self, token_id):
        if token_id == MASTER_API_TOKEN:
            return StubGlobalApi()
        elif token_id == 'user-magic':
            return StubUserApi()
        else:
            raise InvalidTokenException(token_id, ["Nope."])

def make_request(path, method='GET'):
    request = HttpRequest()
    request.path = path
    request.method = method
    request.session = {}
    return request

def app_view(request):
    return HttpResponse("Hi!")

class TestApiEndpointDecorator(SimpleTestCase):
    def test_401_without_token(self):
        app = ApiEndpoint(None, auth_factory=MockAuthorizer)
        response = app(make_request('/'))
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response['WWW-Authenticate'], 'Bearer')

    def test_401_with_bogus_token(self):
        app = ApiEndpoint(None, auth_factory=MockAuthorizer)
        request = make_request('/')
        request.META['Authorization'] = 'Bearer: not-a-real-token'
        response = app(request)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response['WWW-Authenticate'], 'Bearer')

    def test_200_successful_admin_token(self):
        def app_view(request):
            self.assertIsInstance(request.api, GlobalApi)
            return HttpResponse("Hi!")

        app = ApiEndpoint(app_view, auth_factory=MockAuthorizer)
        request = make_request('/')
        request.META['Authorization'] = 'Bearer: {}'.format(MASTER_API_TOKEN)
        response = app(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"Hi!")

    def test_200_successful_user_token(self):
        def app_view(request):
            self.assertIsInstance(request.api, UserApi)
            return HttpResponse("Hi!")

        app = ApiEndpoint(app_view, auth_factory=MockAuthorizer)
        request = make_request('/')
        request.META['Authorization'] = 'Bearer: {}'.format('user-magic')
        response = app(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"Hi!")

    def test_mangled_header(self):
        app = ApiEndpoint(None, auth_factory=MockAuthorizer)
        request = make_request('/')
        request.META['Authorization'] = 'Boarer: {}'.format(MASTER_API_TOKEN)
        response = app(request)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response['WWW-Authenticate'], 'Bearer')

    def test_lenient_input(self):
        def app_view(request):
            self.assertIsInstance(request.api, GlobalApi)
            return HttpResponse("Hi!")

        app = ApiEndpoint(app_view, auth_factory=MockAuthorizer)
        request = make_request('/')
        request.META['Authorization'] = 'bearer: {}'.format(MASTER_API_TOKEN)
        response = app(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"Hi!")
