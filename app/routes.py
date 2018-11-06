from app import app

@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"

# let's make a merge conflict