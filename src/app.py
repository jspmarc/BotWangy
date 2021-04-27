# flask
from flask import Flask, send_from_directory, jsonify
from flask.globals import request
# dotenv
from dotenv import load_dotenv
# firebase
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
# others
import re
from matching import boyer_moore
from response import lihat_tugas, handle_bingung

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def hello():
    return send_from_directory('view/public', 'index.html')


@app.route("/<path:path>")
def home(path):
    return send_from_directory('view/public', path)


@app.route("/send_msg")
def respond():
    # asumsi msg udah dibersihin dari front-end
    msg = str(request.args.get('msg')).lower()
    msg = re.sub(r'[^\s\w:./,\-]', '', msg)
    msg = re.sub(r'\s{2,}', '', msg)

    user_mau = dict()
    user_mau['tambah_task'] = False
    user_mau['lihat_task'] = False
    user_mau['lihat_deadline'] = False
    user_mau['update_task'] = False
    user_mau['nandain_task_selesai'] = False
    user_mau['lihat_help'] = False

    # Tentuin user mau ngapain
    # Cek mau liat task apa bukan
    trigger_liat_task = [
        'apa saja',
    ]

    for trigger in trigger_liat_task:
        if boyer_moore(text=msg, pattern=trigger) != -1:
            user_mau['lihat_task'] = True
            break

    # Untuk di-return ke front-end, harus memiliki 'msg'
    ret = dict()

    try:
        if user_mau['tambah_task']:
            pass
        elif user_mau['lihat_task']:
            ret['msg'] = lihat_tugas(msg, db)
        elif user_mau['lihat_deadline']:
            pass
        elif user_mau['update_task']:
            pass
        elif user_mau['nandain_task_selesai']:
            pass
        elif user_mau['lihat_help']:
            pass
        else:  # kasih error
            ret['msg'] = handle_bingung()
    except ValueError or KeyError:
        ret['msg'] = handle_bingung()

    return jsonify(ret)


if __name__ == '__main__':
    load_dotenv()

    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred, {
        'projectId': 'bot-wangy',
    })
    db = firestore.client()

    app.run(port=8080, debug=True)
