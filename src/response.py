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
    month_regex =\
            r'(januari|februari|maret|april|mei|juni|juli|agustus|september|oktober|november|desember)'
    regex_group1 = r'\d{1,2}(\/|-)\d{1,2}(\/|-)\d{2,4}'
    regex_group2 = r'\d{1,2} ' + month_regex + r' \d{2,4}'
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

        if re.search(regex_group2, clean, flags=re.IGNORECASE) is not None:
            clean = clean.split(' ')
            date = clean[0]
            try:
                month = month_no[clean[1].lower()]
            except KeyError:
                month = '1' # TODO: GANTI INI
            year = clean[2]
            clean = date + '/' + month + '/' + year

        clean = re.sub('-', '/', clean)

        try:
            matches.append(datetime.strptime(clean, '%d/%m/%y'))
        except ValueError:
            matches.append(datetime.strptime(clean, '%d/%m/%Y'))
            # try:
            #     matches.append(datetime.strptime(clean, '%d/%m/%Y'))
            # except ValueError:
            #     # TODO: GANTI INI
            #     matches.append(datetime.now(ZoneInfo('Asia/Jakarta')))

    return matches


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


if __name__ == '__main__':
    coba = 'Hari ini tanggal 27 April 2021 : 27/04/2021 : 27-04-2021'
    print(get_date(coba))
