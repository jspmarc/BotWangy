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


@app.route("/send_msg")
def respond():
    # asumsi msg udah dibersihin dari front-end
    msg = str(request.args.get('msg')).lower()
    msg = re.sub(r'[^\s\w:./,\-]', '', msg)
    msg = re.sub(r'_', ' ', msg)
    keywords = load_keywords()

    user_mau = dict()
    user_mau['tambah_task'] = False
    user_mau['lihat_task'] = False
    user_mau['lihat_deadline'] = False
    user_mau['update_task'] = False
    user_mau['nandain_task_selesai'] = False
    user_mau['lihat_help'] = False

    # Tentuin dia mau lihat task apa bukan

    # Untuk di-return ke front-end, harus memiliki 'msg'
    ret = dict()

    if user_mau['tambah_task']:
        pass
    elif user_mau['lihat_task']:
        ret['msg'] = lihat_tugas(msg)
    elif user_mau['lihat_deadline']:
        pass
    elif user_mau['update_task']:
        pass
    elif user_mau['nandain_task_selesai']:
        pass
    elif user_mau['lihat_help']:
        pass
    else:  # kasih error
        ret['msg'] = 'Maaf, aku ga paham kamu ngomong apa 😟'

    return jsonify(ret)


def load_keywords() -> 'dict[str, list[str]]':
    '''
    Fungsi untuk loading keywords dari database

    Returns
    -------
    dict[str, list[str]]
        dictionary dengan key adalah jenis keyword dan value adalah array
        of string untuk keyword-nya
    '''
    # load keyword untuk jenis tugas
    jenis_tugas_ref = db.collection(u'keywords').document(u'jenis_tugas')
    keywords = dict()
    keywords['jenis_tugas'] = jenis_tugas_ref.get().to_dict()['keywords']

    return keywords


def lihat_tugas(msg: str) -> str:
    '''
    Fungsi untuk mendapatkan list tugas dari database

    Parameters
    ----------
    msg : str
        message dari user

    Returns
    -------
    str
        balasan dari bot
    '''
    tugas_ref = db.collection(u'tugas')
    all_tugas = tugas_ref.stream()
    res = "[Daftar tugas IF'19]\n"

    i = 1
    for tugas in all_tugas:
        tugas_dict = tugas.to_dict()

        if (tugas_dict['selesai']):
            continue

        res += f'{i}. ID: {tugas.id}'

        if tugas_dict['jenis'] == 'tubes':
            jenis = 'tugas besar'
        elif tugas_dict['jenis'] == 'tucil':
            jenis = 'tugas_kecil'
        elif tugas_dict['jenis'] == 'kuis':
            jenis = 'kuis'
        elif tugas_dict['jenis'] == 'ujian':
            jenis = 'ujian'
        else:
            jenis = 'praktikum'

        res += f'\n\t{tugas_dict["deadline"]} {tugas_dict["id_matkul"]}: {jenis} - {tugas_dict["topik"]}'
        res += '\n'
        i += 1

    return res


if __name__ == '__main__':
    load_dotenv()

    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred, {
        'projectId': 'bot-wangy',
    })
    db = firestore.client()

    print(load_keywords())

    app.run(port=8080, debug=True)
