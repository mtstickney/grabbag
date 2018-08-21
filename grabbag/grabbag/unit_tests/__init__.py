from django.test import SimpleTestCase
from django.http import HttpRequest, HttpResponseNotFound, HttpResponse
from django.urls import Resolver404

from grabbag.middleware import BogonFilter
from grabbag.decorators import login_required

def make_request(path, method='GET'):
    request = HttpRequest()
    request.path = path
    request.method = method
    request.session = {}
    return request

class TestBogonFilterMiddleware(SimpleTestCase):
    def test_404_returned(self):
        def app_view(request):
            return HttpResponseNotFound()

        app_middleware = BogonFilter(app_view)
        response = app_middleware(make_request('/exists/'))

        self.assertEquals(response.status_code, 404)

    def test_200_returned(self):
        app_called = False

        def app_view(request):
            nonlocal app_called
            app_called = True
            return HttpResponse("Yep, it works")

        app_middleware = BogonFilter(app_view)
        response = app_middleware(make_request('/exists/'))

        self.assertTrue(app_called)
        self.assertEquals(response.status_code, 200)

    def test_short_circuit_on_404(self):
        def app_view (request):
            self.fail("App was called ")

        app_middleware = BogonFilter(app_view)
        with self.assertRaises(Resolver404):
            response = app_middleware(make_request('/does_not_exist/'))

class TestLoginRedirects(SimpleTestCase):
    def test_anonymous_redirect(self):
        def app_view(request):
            return HttpResponse("Whee!")

        wrapped = login_required(app_view)
        request = make_request('/the/url/?param=value')
        response = wrapped(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/login/?url=%2Fthe%2Furl%2F%3Fparam%3Dvalue')

    def test_bogus_redirect_url(self):
        def app_view(request):
            return HttpResponse("Whee!")

        wrapped = login_required(app_view)
        request = make_request('http://foo.com/bar/')
        request.session['logged_in'] = True
        response = wrapped(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"Whee!")
