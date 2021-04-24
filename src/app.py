from flask import Flask, send_from_directory, jsonify
from flask.globals import request
from matching import boyer_moore

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def hello():
    return send_from_directory('view/public', 'index.html')


@app.route("/<path:path>")
def home(path):
    return send_from_directory('view/public', path)


@app.route("/kalidua")
def kalidua():
    no = int(str(request.args.get('no'))) * 2
    return jsonify(result=no)


@app.route("/match")
def match():
    text = str(request.args.get('text'))
    pattern = str(request.args.get('pattern'))

    return jsonify(index_start=boyer_moore(pattern, text))


if __name__ == '__main__':
    app.run(port=8080, debug=True)
