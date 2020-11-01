from webpy.urls import Router

user_router = Router()


@user_router.route('/home')
def home(req, resp):
    resp.text = 'Hello world!'


