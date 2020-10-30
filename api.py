from webob import Request, Response
from parse import parse
import inspect


class WebAPI(object):
    def __init__(self):
        self.routes = dict()

    def __call__(self, environ, start_response):
        request = Request(environ)

        response = self.handle_request(request)

        return response(environ, start_response)

    def handle_request(self, request):
        response = Response()

        handler, params = self.find_handler(request_path=request.path)

        if handler is not None:
            if inspect.isclass(handler):
                handler_function = getattr(handler(), request.method.lower(), None)
                assert handler_function is not None, AttributeError("Method not allowed", request.method)
            else:
                handler(request, response, **params)
        else:
            self.default_response(response)

        return response

    def find_handler(self, request_path):
        for path, handler in self.routes.items():
            parse_results = parse(path, request_path)
            if parse_results is not None:
                return handler, parse_results.named
        return None, None

    def default_response(self, response):
        response.status_code = 404
        response.text = "Not found."

    def route(self, path):
        assert path not in self.routes, AssertionError("Such route already exists.")
        def wrapper(handler):
            self.routes[path] = handler
            return handler
        return wrapper
