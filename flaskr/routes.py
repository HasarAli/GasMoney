from flaskr import app

@app.route('/')
def index():
    return '<h1>Hey There!</h1>'
