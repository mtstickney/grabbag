from django.test import SimpleTestCase
from django.http import HttpRequest, HttpResponseNotFound, HttpResponse
from django.urls import Resolver404

from grabbag.middleware import BogonFilter

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
