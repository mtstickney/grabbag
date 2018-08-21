from django.shortcuts import redirect
from django.urls import reverse

from urllib.parse import urlparse, urlunparse, urlencode, ParseResult

def sanitize_redirect_url(url):
    untrusted = urlparse(url)
    redirect_url = ParseResult(
        scheme='',
        netloc='',
        path=untrusted.path if untrusted.path != '' else '/',
        params=untrusted.params,
        query=untrusted.query,
        fragment=untrusted.fragment
    )

    redirect_str = urlunparse(redirect_url)
    return redirect_str if redirect_str != '' else None

def login_required(view):
    def require_login(request):
        if 'logged_in' in request.session:
            return view(request)
        else:
            login_url = reverse('user-login')
            url = urlparse(login_url)
            redirect_url = ParseResult(
                scheme=url.scheme,
                netloc=url.netloc,
                path=url.path,
                params=url.params,
                fragment=url.fragment,
                query=urlencode({'url': sanitize_redirect_url(request.path)})
            )

            return redirect(urlunparse(redirect_url))
    return require_login
