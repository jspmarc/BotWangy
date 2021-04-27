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


def get_date(msg: str) -> 'list[datetime]':
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
    >>> get_date('tanggal 27-April/2021')
    [datetime.datetime(2021, 4, 27, 0, 0)]
    >>> get_date('tanggal 27/04-21')
    [datetime.datetime(2021, 4, 27, 0, 0)]
    >>> get_date('tanggal 27-04 21')
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
    def fail(saat: str) -> str:
        '''
        Melakukan subroutine ketika menjadi kegagalan

        Returns
        -------
        str
            Pesan error
        '''
        print(f'[List tugas] Error saat {saat}: {msg}')
        return 'Gagal memehami periode/durasi pesan 😵'

    tugas_ref = db.collection(u'tugas')
    all_tugas = tugas_ref.stream()
    res = "[Daftar tugas IF'19]\n"

    # ngertiin message user
    trigger_tanggal_satuan = [
        'ke depan',
        'berikutnya',
        'lagi',
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
            pake_tanggal_satuan = boyer_moore(text=msg, pattern=trigger) != -1
            if pake_tanggal_satuan:
                break

    # Tentuin user-nya mau jenis task (tugas) tertentu atau nggak
    matching_patt = None
    jenis_tugas = load_keywords(db)['jenis_tugas']
    print(jenis_tugas)
    for jenis in jenis_tugas:
        if boyer_moore(text=msg, pattern=jenis) != -1:
            matching_patt = jenis

    i = 1
    for tugas in all_tugas:
        tugas_dict = tugas.to_dict()

        if (tugas_dict['selesai']):
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
        if pake_tanggal_satuan:
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
                return fail('mendapatkan trigger periode')

            try:
                durasi = int(re.findall(r'\d+', msg[:idx_periode])[0])
            except IndexError:
                return fail('mendapatkan waktu pada tanggal satuan')

            if periode == 'minggu':
                durasi *= 7
            elif periode == 'bulan':
                durasi *= 30
            elif periode == 'tahun':
                durasi *= 365

            # Tetep tunjukin tugas yang udah lewat deadline
            now = datetime.now().replace(microsecond=0)
            if deadline > now + timedelta(days=durasi):
                continue

        elif pake_tanggal_range:
            try:
                date1, date2, *_ = get_date(msg)
            except ValueError:
                return fail('mendapatkan tanggal pada tanggal range')
            if deadline <= date1 or deadline >= date2:
                # Deadline di luar permintaan user
                continue

        if tugas_dict['jenis'] == 'tubes':
            jenis = 'tugas besar'
        elif tugas_dict['jenis'] == 'tucil':
            jenis = 'tugas kecil'
        else:
            jenis = tugas_dict['jenis']

        if matching_patt is not None and matching_patt != jenis:
            continue

        space_4 = '    '
        res += f'{i}. ID: {tugas.id}'
        res += f'\n{space_4}Matkul: {tugas_dict["id_matkul"]}'
        res += f'\n{space_4}Deadline (yyyy/mm/dd): {deadline_str}'
        res += f'\n{space_4}{jenis}: {tugas_dict["topik"]}'
        res += '\n\n'
        i += 1

    return res


def handle_bingung():
    return 'Maaf, aku ga paham kamu ngomong apa 😵'


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
    ret += 'Kata kunci (tanpa "): \n'
    ret += '2. Melihat daftar tasks yang harus dikerjakan.\n'
    ret += 'Kata kunci (tanpa "): "apa saja"\n'
    ret += '3. Menampilkan deadline dari suatu task tertentu.\n'
    ret += 'Kata kunci (tanpa "): "kapan"\n'
    ret += '4. Memperbarui task tertentu.\n'
    ret += 'Kata kunci (tanpa "): \n'
    ret += '5. Menandai bahwa suatu task sudah selesai dikerjakan.\n'
    ret += 'Kata kunci (tanpa "): \n'
    ret += '6. Menampilkan opsi help yang difasilitasi oleh assistant.\n'
    ret += 'Kata kunci (tanpa "): \n'
    ret += '7. Mendefinisikan list kata penting terkait tugas.\n'
    ret += 'Kata kunci (tanpa "): "tolong", "help", "助けて", "tasukete"\n'
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
    print(get_date(coba))
