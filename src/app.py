# flask
from flask import Flask, send_from_directory, jsonify
from flask.globals import request
# dotenv
from dotenv import load_dotenv
# firebase
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
# app's modules
from matching import boyer_moore

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def hello():
    return send_from_directory('view/public', 'index.html')


@app.route("/<path:path>")
def home(path):
    return send_from_directory('view/public', path)


@app.route("/match")
def match():
    text = str(request.args.get('text'))
    pattern = str(request.args.get('pattern'))

    return jsonify(index_start=boyer_moore(pattern, text))


@app.route("/get_tugas")
def get_tugas():
    tugas_ref = db.collection(u'tugas')
    all_tugas = tugas_ref.stream()
    tugas_dict = dict()

    for tugas in all_tugas:
        # print(f'{tugas.id} => {tugas.to_dict()}')
        tugas_dict[tugas.id] = tugas.to_dict()

    return jsonify(tugas_dict)


if __name__ == '__main__':
    load_dotenv()

    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred, {
        'projectId': 'bot-wangy',
    })
    db = firestore.client()

    app.run(port=8080, debug=True)
