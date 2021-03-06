'''
Module untuk membantu dalam 'menjawab' query/request user

Reinaldo Antolis / 13519015
Jeane Mikha / 13519116
Josep Marcello / 13519164

27 April 2021
'''

from datetime import datetime, timedelta
from matching import boyer_moore
import re


def extract_date(msg: str) -> 'list[datetime]':
    '''
    Fungsi untuk mengekstrak tanggal dari string. Format tanggal yang valid:
    <tanggal/nomor hari><delimiter><bulan><delimiter><tahun>
    delimiter valid: `-`, `/`, ` `
    tanggal valid: 1 atau 01 sampai 31
    bulan valid: nama-nama bulan dalam bahasa Indonesia,
                 nomor bulan 01 atau 1 sampai 12
    tahun valid: dua digit terakhir tahun atau 4 digit (21 atau 2021)
    Contoh tanggal valid:
    - 28 April 2021
    - 28 04 2021
    - 28 04 21
    - 28/04/2021
    - 28/4/21
    - 08/4/21
    - 8/4/21
    - 28-April-2021
    - 28/April/2021
    - 28/04-21
    - 28-April/21

    Parameters
    ----------
    msg : str
        string yang mau diekstrak tanggalnya

    Returns
    -------
    list[datetime]
        list of datetime berisikan semua tanggal pada string yang ditemukan
        secara berurut

    Throws
    ------
    KeyError
        Kalau nama bulan invalid (tidak sesuai dengan KBBI)
    ValueError
        Kalau format tanggal salah

    Examples
    --------
    >>> extract_date('tanggal 27-April/2021')
    [datetime.datetime(2021, 4, 27, 0, 0)]
    >>> extract_date('tanggal 27/04-21')
    [datetime.datetime(2021, 4, 27, 0, 0)]
    >>> extract_date('tanggal 27-04 21')
    [datetime.datetime(2021, 4, 27, 0, 0)]
    '''
    month_regex =\
        r'(januari|februari|maret|april|mei|juni|juli|agustus|september|oktober|november|desember)'
    regex_separator = r'(\/|-| )'  # matches `/` or `-` or `space`
    regex_group1 = r'\d{1,2}' + regex_separator + r'\d{1,2}' +\
        regex_separator + r'\d{2,4}'
    regex_group2 = r'\d{1,2}' + regex_separator + month_regex +\
        regex_separator + r'\d{2,4}'
    regex_all = r'(' + regex_group1 + r'|' + regex_group2 + r')'

    month_no = {
        'januari': '1',
        'februari': '2',
        'maret': '3',
        'april': '4',
        'mei': '5',
        'juni': '6',
        'juli': '7',
        'agustus': '8',
        'september': '9',
        'oktober': '10',
        'november': '11',
        'desember': '12',
    }

    matches_dirty = re.findall(regex_all, msg, flags=re.IGNORECASE)

    matches = []

    for match in matches_dirty:
        clean = match[0]

        clean = re.findall(r'[^ /\-]+', clean)
        clean = '/'.join(clean)
        if re.search(regex_group2, clean, flags=re.IGNORECASE) is not None:
            clean = clean.split('/')
            date = clean[0]
            month = month_no[clean[1].lower()]
            year = clean[2]
            clean = date + '/' + month + '/' + year

        try:
            matches.append(datetime
                           .strptime(clean, '%d/%m/%y'))
        except ValueError:
            matches.append(datetime
                           .strptime(clean, '%d/%m/%Y'))

    return matches


def extract_jenis(msg: str, db) -> str:
    '''
    Fungsi untuk mendapatkan jenis tugas dari string. Mengembalikan jenis tugas
    yang dimaksud user. Jika jenis tugas tidak jelas atau tidak ada, maka akan
    dikembalikan string kosong.
    Jenis tugas yang ada:
        - uas
        - uts
        - praktikum (atau prak)
        - tubes (atau tugas besar)
        - tucil (atau tugas kecil)
        - kuis (atau quiz)

    Parameters
    ----------
    msg : str
        pesan/message dari user
    db : firestore database
        database untuk mendapatkan data

    Returns
    -------
    str
        jenis user yang sebenarnya (uts, uas, praktikum, tubes, tucil, kuis)
    '''
    possible_keywords = load_keywords(db)['jenis_tugas']
    regex_kata_kunci = '('
    i = 0
    for keyword in possible_keywords:
        regex_kata_kunci += keyword
        regex_kata_kunci += '|' if i < len(possible_keywords) - 1 else ''
        i += 1
    regex_kata_kunci += ')'
    regex = regex_kata_kunci + r'|(prak|tugas kecil|tugas besar|quiz)'
    try:
        match = re.findall(regex, msg, flags=re.IGNORECASE)[0]
        if len(match[0]) == 0:
            if match[1] == 'prak':
                match = 'praktikum'
            elif match[1] == 'quiz':
                match = 'kuis'
            elif match[1] == 'tugas kecil':
                match = 'tucil'
            elif match[1] == 'tugas besar':
                match = 'tubes'
            else:
                match = ''
        else:
            match = match[0]
    except IndexError:
        match = ''

    return match


def extract_course_id(msg: str) -> str:
    '''
    Fungsi untuk mendapatkan kode mata kuliah

    Parameters
    ----------
    msg : str
        pesan/message dari user

    Returns
    -------
    str
        kode mata kuliah (ITB)
    '''
    matches = re.findall(r'[a-zA-Z]{2}\d{4}', msg, flags=re.IGNORECASE)

    try:
        res = matches[0]
    except IndexError:
        res = None
    return res.upper()


def extract_topic(msg: str) -> str:
    '''
    Fungsi untuk mencari topic yang terletak
    antara tanda kutip

    Parameters
    ----------
    msg : str
        pesan/message dari user

    Returns
    -------
    str
        topic

    Throws
    ------
    ValueError
        Kalau message tidak memiliki kode mata kuliah
    '''
    try:
        topic = re.findall(r'"[\w\s:\',.?!><\]\[\}\{=+\-\)\(;]+"', msg)
        res = re.sub(r'"', '', topic[0])
    except IndexError:
        res = None
    return res


def load_keywords(db) -> 'dict[str, list[str]]':
    '''
    Fungsi untuk loading keywords dari database

    Parameters
    ----------
    db : firestore database
        database untuk mendapatkan data

    Returns
    -------
    dict[str, list[str]]
        dictionary dengan key adalah jenis keyword dan value adalah array
        of string untuk keyword-nya
    '''
    # load keyword untuk jenis tugas
    jenis_tugas_ref = db.collection(u'keywords').document(u'keywords')
    keywords = jenis_tugas_ref.get().to_dict()

    return keywords


def lihat_tugas(msg: str, db) -> str:
    '''
    Fungsi untuk mendapatkan list tugas dari database. Bisa dengan periode
    tertentu.
    Bisa dengan durasi (inklusif), seperti:
        <dari|antara> <tanggal 1> <hingga|sampai> <tanggal 2>
    Bisa juga dari sekarang sampai jangka waktu tertentu, seperti:
        <n> <hari|minggu|bulan|tahun> <ke depan|berikutnya|lagi>
    Apa bila bentuk query/msg adalah:
    `deadline apa saja dari 24/04/2021 sampai 30/04/2021 3 minggu ke depan?`
    atau
    `deadline apa saja 3 minggu ke depan dari 24/04/2021 sampai 30/04/2021?`
    maka yang hanya akan ditunjukkan adalah deadline dari atnggal 24 April 21
    sampai 30 April 2021 (inklusif)

    Parameters
    ----------
    msg : str
        message dari user
    db : firestore database
        database untuk mendapatkan data

    Returns
    -------
    str
        balasan dari bot

    Throws
    ------
    KeyError
        Kalau nama bulan pada msg invalid (tidak sesuai dengan KBBI)
    ValueError
        Kalau format tanggal pada msg salah
    '''
    tugas_ref = db.collection(u'tugas')
    all_tugas = tugas_ref.stream()
    res = "[Daftar tugas IF'19]\n"

    # ngertiin message user
    trigger_tanggal_satuan = [
        'ke depan',
        'berikutnya',
        'lagi',
        'selanjutnya',
    ]

    trigger_tanggal_range_dari = [
        'dari',
        'antara',
    ]

    trigger_tanggal_range_sampai = [
        'hingga',
        'sampai',
    ]

    pake_tanggal_range = False
    pake_tanggal_satuan = False

    # Cek user-nya mau deadline pada periode tertentu atau nggak
    found = False
    idx_keyword_tanggal_range_dari = -1
    for trigger_dari in trigger_tanggal_range_dari:
        idx_keyword_tanggal_range_dari =\
            boyer_moore(text=msg, pattern=trigger_dari)
        found = idx_keyword_tanggal_range_dari != -1
        if found:
            break

    found = False
    idx_keyword_tanggal_range_sampai = -1
    for trigger_sampai in trigger_tanggal_range_sampai:
        idx_keyword_tanggal_range_sampai =\
            boyer_moore(text=msg, pattern=trigger_sampai)
        found = idx_keyword_tanggal_range_sampai != -1
        if found:
            break

    pake_tanggal_range =\
        idx_keyword_tanggal_range_dari != -1\
        and idx_keyword_tanggal_range_sampai != -1\
        and idx_keyword_tanggal_range_dari <= idx_keyword_tanggal_range_sampai\

    if not pake_tanggal_range:
        for trigger in trigger_tanggal_satuan:
            if boyer_moore(text=msg, pattern=trigger) != -1:
                pake_tanggal_satuan = True
                trigger_periode = [
                    'hari',
                    'minggu',
                    'bulan',
                    'tahun',
                ]

                for trigger in trigger_periode:
                    idx_periode = boyer_moore(text=msg, pattern=trigger)
                    if idx_periode != -1:
                        periode = trigger
                        break

                if idx_periode == -1:
                    return 'Durasi waktu kamu salah'

                try:
                    durasi = int(re.findall(r'\d+', msg[:idx_periode])[0])
                except IndexError:
                    return 'Durasi waktu kamu salah'

                if periode == 'minggu':
                    durasi *= 7
                elif periode == 'bulan':
                    durasi *= 30
                elif periode == 'tahun':
                    durasi *= 365

    else:
        try:
            date1, date2, *_ = extract_date(msg)
            if date1 > date2:
                return 'Jarak tanggal kamu salah'
        except ValueError:
            return 'Penulisan tanggal kamu salah'

    # Tentuin user-nya mau jenis task (tugas) tertentu atau nggak
    jenis_tugas_permintaan = extract_jenis(msg, db)

    i = 1
    for tugas in all_tugas:
        tugas_dict = tugas.to_dict()

        if len(jenis_tugas_permintaan) != 0\
                and tugas_dict['jenis'] != jenis_tugas_permintaan:
            continue

        # bikin deadline
        deadline = tugas_dict['deadline']
        year, month, day, hour, minute, second =\
            deadline.year,\
            deadline.month,\
            deadline.day,\
            deadline.hour,\
            deadline.minute,\
            deadline.second
        deadline = datetime(year, month, day, hour, minute, second)
        deadline_str = deadline.strftime('%Y-%m-%d')

        # cek tanggal permintaan user
        # print(date1, deadline, date2)
        if pake_tanggal_satuan:
            # Tetep tunjukin tugas yang udah lewat deadline
            print(durasi)
            now = datetime.now().replace(hour=23, minute=59, second=59, microsecond=0)
            if deadline > now + timedelta(days=durasi):
                continue
        elif pake_tanggal_range:
            if deadline < date1 or deadline > date2:
                # Deadline di luar permintaan user
                continue

        if tugas_dict['jenis'] == 'tubes':
            jenis = 'tugas besar'
        elif tugas_dict['jenis'] == 'tucil':
            jenis = 'tugas kecil'
        else:
            jenis = tugas_dict['jenis']

        space_4 = '    '
        res += f'{i}. ID: {tugas.id}'
        res += f'\n{space_4}Matkul: {tugas_dict["id_matkul"]}'
        res += f'\n{space_4}Deadline (yyyy-mm-dd): {deadline_str}'
        res += f'\n{space_4}{jenis}: {tugas_dict["topik"]}'
        res += '\n\n'
        i += 1

    if i == 1:
        res = 'Ga ada deadline yang akan datang\n'

    return res[:-1]


def lihat_deadline(msg: str, db) -> str:
    '''
    Fungsi untuk mendapatkan deadline tugas-tugas dari sebuah matkul

    Parameters
    ----------
    msg : str
        message dari user
    db : firestore database
        database untuk mendapatkan data

    Returns
    -------
    str
        balasan dari bot

    Throws
    ------
    KeyError
        Kalau nama bulan pada msg invalid (tidak sesuai dengan KBBI)
    ValueError
        Kalau format tanggal pada msg salah
    '''
    id_matkul_request = extract_course_id(msg)
    if id_matkul_request is None:
        return 'ID Matkul ga ada atau salah'
    jenis_tugas_request = extract_jenis(msg, db)
    if jenis_tugas_request == '':
        return 'Jenis tugas salah'

    ret = f'Deadline {jenis_tugas_request} {id_matkul_request}:\n'
    tugas_ref = db.collection(u'tugas')
    all_tugas = tugas_ref.stream()

    i = 1
    for tugas in all_tugas:
        tugas = tugas.to_dict()
        if tugas['jenis'] != jenis_tugas_request\
           or tugas['id_matkul'].lower() != id_matkul_request.lower():
            continue
        deadline_dirty = tugas['deadline']
        deadline = datetime(
            day=deadline_dirty.day,
            month=deadline_dirty.month,
            year=deadline_dirty.year
        ).strftime('%Y-%m-%d')
        ret += f'{i}. {deadline}\n'
        i += 1

    if i == 1:
        ret = f'Tidak ada deadline untuk {jenis_tugas_request} matkul {id_matkul_request}.'
    return ret


def tambah_tugas(msg: str, db) -> str:
    '''
    Fungsi untuk menambahkan list tugas ke database

    Parameters
    ----------
    msg : str
        message dari user
    db : firestore database
        database untuk mendapatkan data

    Returns
    -------
    str
        balasan dari bot
        ID, tanggal, kode mata kuliah, jenis tugas, topik tugas

    Throws
    ------
    ValueError
        Jika msg kurang 1 atau lebih komponen
        (tanggal, kode mata kuliah, jenis, topik tugas)
    '''
    date = extract_date(msg)[0]
    course_id = extract_course_id(msg)
    jenis = extract_jenis(msg, db)
    topic = extract_topic(msg)
    if course_id is None or jenis == '' or topic is None:
        raise ValueError(f'{"ID Matkul" if course_id is None else "Jenis tugas" if jenis == "" else "Topik tugas"} salah')

    tanggal = date.strftime('%Y-%m-%d')

    data = {
        u'deadline': date,
        u'id_matkul': course_id,
        u'jenis': jenis,
        u'topik': topic
    }

    tugas_ref = db.collection(u'tugas')
    all_tugas = tugas_ref.stream()

    id_task = '1'
    for tugas in all_tugas:
        id_task = str(int(tugas.id) + 1)

    ret =  '[Task berhasil dicatat]'
    ret += f'\nID: {id_task}'
    ret += f'\nMatkul: {course_id}'
    ret += f'\nDeadline (yyyy/mm/dd): {tanggal}'
    ret += f'\nJenis: {jenis}'
    ret += f'\nTopik: {topic}'

    db.collection(u'tugas').document(id_task).set(data)

    return ret


def easter_egg():
    try:
        with open('view/public/copypasta.txt', 'r') as f:
            msg = f.read()
    except Exception:
        msg = '????????? ??? ???\\(\'0\')/??? ??? ????????? FLIP ALL THE TABLES'
    return msg


def update_tugas(msg: str, db) -> str:
    task_id = extract_task_id(msg)
    date_list = extract_date(msg)
    print(task_id, date_list)
    # Kasus tidak dituliskan ID dari tugas yang ingin diundur deadlinenya
    if task_id is None or len(date_list) == 0:
        return f'{"ID Tugas" if task_id is None else "Tanggal"} kamu salah'

    date = date_list[0]

    all_tugas_ref = db.collection(u'tugas')
    all_tugas = all_tugas_ref.stream()
    tugas_found = False
    for tugas in all_tugas:
        if task_id == tugas.id:
            tugas.reference.update({u'deadline': date})
            tugas_found = True
            break

    if tugas_found:
        res = "Deadline tugas " + task_id + " berhasil diundur"
    else:
        res = "Tugas " + task_id + " tidak terdapat dalam daftar tugas"
    # TODO: Write ke firebase db

    return res


def clear_tugas(msg: str, db) -> str:
    task_id = extract_task_id(msg)
    # Kasus tidak dituliskan ID dari tugas yang ingin ditandai selesai
    if task_id is None:
        return 'ID tugas kamu salah'

    all_tugas_ref = db.collection(u'tugas')
    all_tugas = all_tugas_ref.stream()
    tugas_found = False
    for tugas in all_tugas:
        if task_id == tugas.id:
            tugas.reference.delete()
            tugas_found = True
            break

    if tugas_found:
        res = "Tugas " + task_id + " berhasil ditandai selesai"
    else:
        res = "Tugas " + task_id + " tidak terdapat dalam daftar tugas"
    # TODO: Write ke firebase db

    return res


def extract_task_id(msg: str) -> str:
    matches = re.findall(r'\d+', msg, flags=re.IGNORECASE)

    try:
        res = matches[0]
    except IndexError:
        res = None
    return res


def handle_bingung():
    return 'Maaf, aku ga paham kamu ngomong apa ????'


def help_msg(db) -> str:
    '''
    Membuat fungsi untuk help message

    Parameters
    ----------
    db : firestore database
        database untuk mendapatkan data

    Returns
    -------
    str
        help message
    '''
    keywords = load_keywords(db)
    jenis_tugas = keywords['jenis_tugas']

    ret = 'It\'s dangerous to go alone! Take this.\n'
    ret += '\n'
    ret += '[Fitur]\n'
    ret += '1. Menambahkan tasks baru.\n'
    ret += f'Kata kunci: {keywords["tambah_task"]}\n'
    ret += '2. Melihat daftar tasks yang harus dikerjakan.\n'
    ret += f'Kata kunci: {keywords["lihat_task"]}\n'
    ret += '3. Menampilkan deadline dari suatu task tertentu.\n'
    ret += f'Kata kunci: {keywords["lihat_deadline"]}\n'
    ret += '4. Memperbarui task tertentu.\n'
    ret += f'Kata kunci: {keywords["update_task"]}\n'
    ret += '5. Menandai bahwa suatu task sudah selesai dikerjakan.\n'
    ret += f'Kata kunci: {keywords["nandain_task_selesai"]}\n'
    ret += '6. Menampilkan opsi help yang difasilitasi oleh assistant.\n'
    ret += f'Kata kunci: {keywords["lihat_help"]}\n'
    ret += '7. Mendefinisikan list kata penting terkait tugas.\n'
    ret += '8. Menampilkan pesan error ketika tidak mengenali query user\n'
    ret += '\n'
    ret += '[Kata kunci tugas]\n'

    i = 1
    for jenis in jenis_tugas:
        ret += f'{i}. {jenis}\n'
        i += 1

    return ret


if __name__ == '__main__':
    coba = 'Hari ini tanggal 27-April/2021 : 27 04/2021 : 27/04-2021'
    print(extract_date(coba))
