from datetime import datetime
from backports.zoneinfo import ZoneInfo
from matching import boyer_moore
import re


def get_date(msg: str) -> 'list[datetime]':
    '''
    Fungsi untuk mengekstrak tanggal dari string

    Parameters
    ----------
    msg : str
        string yang mau diekstrak tanggalnya

    Returns
    -------
    list[datetime]
        list of datetime berisikan semua tanggal pada string yang ditemukan
        secara berurut
    '''
    return re.findall(r'', msg)


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
    print(keywords)

    return keywords


def lihat_tugas(msg: str, db) -> str:
    '''
    Fungsi untuk mendapatkan list tugas dari database

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
    '''
    tugas_ref = db.collection(u'tugas')
    all_tugas = tugas_ref.stream()
    res = "[Daftar tugas IF'19]\n"

    # ngertiin message user
    trigger_tanggal = [
        'ke depan',
        'selanjutnya',
        'lagi',
        'dari',
        'antara'
    ]

    pake_tanggal = False
    for trigger in trigger_tanggal:
        pake_tanggal = boyer_moore(text=msg, pattern=trigger)
        if pake_tanggal:
            break

    i = 1
    for tugas in all_tugas:
        tugas_dict = tugas.to_dict()

        if (tugas_dict['selesai']):
            continue

        res += f'{i}. ID: {tugas.id}'

        if not pake_tanggal:
            deadline = tugas_dict['deadline']
            year, month, day, hour, minute, second, tzinfo =\
                deadline.year,\
                deadline.month,\
                deadline.day,\
                deadline.hour,\
                deadline.minute,\
                deadline.second,\
                deadline.tzinfo
            deadline = datetime(year, month, day, hour, minute, second,
                                tzinfo=tzinfo)\
                .astimezone(ZoneInfo('Asia/Jakarta'))\
                .strftime('%Y-%m-%d')

        if tugas_dict['jenis'] == 'tubes':
            jenis = 'tugas besar'
        elif tugas_dict['jenis'] == 'tucil':
            jenis = 'tugas_kecil'
        elif tugas_dict['jenis'] == 'pr':
            jenis = 'pr'
        else:
            jenis = tugas_dict['jenis']

        space_4 = '    '
        res += f'\n{space_4}Matkul: {tugas_dict["id_matkul"]}'
        res += f'\n{space_4}Deadline: {deadline} WIB'
        res += f'\n{space_4}{jenis}: {tugas_dict["topik"]}'
        res += '\n\n'
        i += 1

    return res
