from webob import Request
from .response import Response
from parse import parse
from requests import Session as RequestSession
from wsgiadapter import WSGIAdapter as RequestsWSGIAdapter
from .templates import get_templates_env
from whitenoise import WhiteNoise
import os
import inspect
from .middleware import Middleware
from .urls import Router
from typing import Dict, ClassVar, Iterable


class WebAPI(object):
    def __init__(self, templates_dir='templates', static_dir='static'):
        self.router = Router()
        self.routes = dict()
        self.templates = get_templates_env(os.path.join(templates_dir))
        self.static_dir = os.path.join(static_dir)
        self.exception_handler = None
        self.whitenoise = WhiteNoise(self.wsgi_app, root=static_dir)
        self.middleware = Middleware(self)

    def __call__(self, environ: Dict, start_response) -> Iterable:
        path_info = environ["PATH_INFO"]

        if path_info.startswith('/static'):
            environ["PATH_INFO"] = path_info[len('/static'):]
            return self.whitenoise(environ, start_response)
        return self.middleware(environ, start_response)

    def wsgi_app(self, environ: Dict, start_response) -> Iterable:
        request = Request(environ)

        response = self.handle_request(request)

        return response(environ, start_response)

    def add_middleware(self, middleware_cls: ClassVar):
        self.middleware.add(middleware_cls)

    def handle_request(self, request: Request) -> Response:
        response = Response()

        handler, params = self._find_handler(request_path=request.path)

        try:
            if handler is not None:
                if inspect.isclass(handler):
                    handler = getattr(handler(), request.method.lower(), None)
                    if handler is None:
                        raise AttributeError("Method now allowed", request.method)

                handler(request, response, **params)
            else:
                self.default_response(response)
        except Exception as e:
            if self.exception_handler is None:
                raise e
            else:
                self.exception_handler(request, response, e)

        return response

    def template(self, template_name: str, context=None) -> str:
        if context is None:
            context = {}

        return self.templates.get_template(template_name).render(**context).encode()

    def test_session(self, base_url: str = "http://testserver") -> RequestSession:
        session = RequestSession()
        session.mount(prefix=base_url, adapter=RequestsWSGIAdapter(self))
        return session

    def add_exception_handler(self, exception_handler):
        self.exception_handler = exception_handler

    def _find_handler(self, request_path: str) -> any and Dict:
        for path, handler in self.router.routes.items():
            parse_results = parse(path, request_path)
            if parse_results is not None:
                return handler, parse_results.named
        return None, None

    def default_response(self, response: Response) -> None:
        response.status_code = 404
        response.text = "Not found."

    def route(self, path: str):
        return self.router.route(path)

    def register_router(self, pattern: str, router: Router) -> None:
        for path, handler in router.routes.items():
            self.router.add_route(f'{pattern}{path}', handler)

    def add_route(self, path: str, handler) -> None:
        self.router.add_route(path, handler)
