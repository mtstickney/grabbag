from django.urls import resolve, Resolver404

class BogonFilter:
    """Short-circuit requests for invalid URLs rather than allowing to be
    processed through the rest of the stack.

    HTTP vulnerability scanners, among others, can make many requests
    at once, and they generally don't save cookies. That means the
    application may think it's receiving a great deal of traffic, and
    may create resources that would be wasted. This middleware
    short-circuits that process by immediately returning a 404
    response for URLs that we know won't be served.

    Note that Django's session middleware is /not/ affected by this
    issue, since sessions aren't created unless some data is actually
    set in the session. Still, other middleware might be affected, so
    this is handy to have around.

    Also note that this check is imperfect: URLs registrations don't
    include information about e.g. what methods they support, and a
    view may always choose to return 404 for reasons that can't be
    predicted. In those cases, the request will pass this filter.
    """

    def __init__(self, get_response):
        self.app = get_response

    def __call__(self, request):
        try:
            resolve(request.path)
        except Resolver404:
            # Don't call into the rest of the app, short-circuit with
            # a 404.
            raise

        return self.app(request)
