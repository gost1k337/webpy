from api import WebAPI

app = WebAPI()


@app.route('/home')
def home(request, response):
    response.text = 'Hello world home page!'


@app.route('/about')
def about(request, response):
    response.text = 'Hello world from about page...'


@app.route('/hello/{person_name}')
def say_hello(request, response, person_name):
    print(person_name)
    response.text = f'hello, {person_name}'
