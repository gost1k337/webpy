class Router(object):
    def __init__(self):
        self.routes = {}

    def route(self, path):
        def wrapper(handler):
            self.add_route(path, handler)
            return handler
        return wrapper

    def add_route(self, path, handler):
        assert path not in self.routes, AssertionError("Such route already exists.")
        self.routes[path] = handler
