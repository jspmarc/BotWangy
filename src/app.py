from flask import Flask, send_from_directory
from flask.globals import request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def hello():
    return send_from_directory('view/public', 'index.html')

@app.route("/<path:path>")
def home(path):
    return send_from_directory('view/public', path)

@app.route("/kalidua")
def double():
    no = str(request.args.get('no'))
    return str(int(no) * 2)

if __name__ == '__main__':
    app.run(port=8080, debug=True)
