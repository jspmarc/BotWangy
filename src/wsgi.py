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
from matching import boyer_moore, levenshtein_distance
from response import (
    lihat_tugas,
    update_tugas,
    clear_tugas,
    handle_bingung,
    help_msg,
    lihat_deadline,
    load_keywords,
    easter_egg,
    tambah_tugas,
)

# global variables
app = Flask(__name__)
load_dotenv()

cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
    'projectId': 'bot-wangy',
})
db = firestore.client()


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
    msg = re.sub(r'[^\s\w:./,\-"]', '', msg)
    msg = re.sub(r'\s{2,}', '', msg)

    user_mau = {}
    user_mau['tambah_task'] = False
    user_mau['lihat_task'] = False
    user_mau['lihat_deadline'] = False
    user_mau['update_task'] = False
    user_mau['nandain_task_selesai'] = False
    user_mau['lihat_help'] = False
    user_mau['easter_egg'] = False

    triggers = load_keywords(db)

    # Tentuin user mau ngapain
    tau_mau_ngapain = False

    def tentuin_mau_apa(aksi, triggers) -> bool:
        ret = False
        if not tau_mau_ngapain:
            for trigger in triggers:
                if trigger == '':
                    continue
                if boyer_moore(text=msg, pattern=trigger) != -1:
                    user_mau[aksi] = True
                    ret = True
                    break

        return ret

    for aksi in user_mau.keys():
        if tau_mau_ngapain:
            break
        user_mau[aksi] = tentuin_mau_apa(aksi, triggers[aksi])
        tau_mau_ngapain = user_mau[aksi]

    # Untuk di-return ke front-end, harus memiliki 'msg'
    ret = dict()

    try:
        if user_mau['tambah_task']:
            ret['msg'] = tambah_tugas(msg, db)
            print('User menambahkan task')
        elif user_mau['lihat_task']:
            ret['msg'] = lihat_tugas(msg, db)
            print('User melihat task')
        elif user_mau['lihat_deadline']:
            ret['msg'] = lihat_deadline(msg, db)
            print('User melihat deadline')
        elif user_mau['update_task']:
            ret['msg'] = update_tugas(msg, db)
            print('User update task')
        elif user_mau['nandain_task_selesai']:
            ret['msg'] = clear_tugas(msg, db)
            print('User menyelesaikan task')
        elif user_mau['lihat_help']:
            ret['msg'] = help_msg(db)
            print('User melihat help')
        elif user_mau['easter_egg']:
            ret['msg'] = easter_egg()
            print('User melihat easter egg')
        else:  # kasih error
            print('Bot bingung')
            ret['msg'] = handle_bingung()

            words = msg.split(' ')
            done = False
            for aksi in user_mau.keys():
                for trigger in triggers[aksi]:
                    for word in words:
                        lev = levenshtein_distance(trigger, word)
                        percantage_diff = lev/len(trigger) * 100
                        if percantage_diff <= 40:
                            ret['msg'] = f'Apakah maksudmu:\n\
                                    "{msg.replace(word, trigger)}"?'
                            done = True
                            break
                    if done:
                        break
                if done:
                    break
    except (ValueError, KeyError, IndexError) as e:
        print('Message user ada yang salah')
        print(e)
        ret['msg'] = handle_bingung()

    print(ret['msg'])
    return jsonify(ret)


if __name__ == '__main__':
    app.run(port=8080, debug=True)
