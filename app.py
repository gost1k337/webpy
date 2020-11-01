from webpy.api import WebAPI
from userRouter import user_router

app = WebAPI(templates_dir='templates')

app.register_router('/blog', user_router)
