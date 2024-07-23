from flask import render_template, Blueprint

app = Blueprint('app', __name__)

@app.route('/health')
def health():
    return 'OK'

@app.route('/')
def index():
    return render_template('index.html')
