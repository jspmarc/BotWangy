'''
Module yang mengandung fungsi matching

Reinaldo Antolis
Jeane Mikha
Josep Marcello

24 April 2021
'''
import string


def find_last_occurance(s: str):
    '''
    Fungsi untuk mendapatkan kemunculan terakhir dari semua karakter pada
    sebuah string

    Parameters
    ----------
    s : str
        string yang ingin dicari kemunculan terakhir setiap karakternya

    Returns
    -------
    dict[str, int]
        dictionary dengan key adalah karakter dan value adalah integer, yaitu
        jumlah kemunculan terakhir karakter pada key
    '''
    ret = dict()

    for c in string.printable:
        ret[c] = -1

    i = 0
    for c in s:
        ret[c] = i
        i += 1

    return ret


def boyer_moore(pattern: str, text: str):
    '''
    Fungsi untuk string matching dengan algoritma Boyer-Moore

    Parameters
    ----------
    pattern : str
        pattern yang ingin dicari pada sebuah string
    text : str
        text string

    Returns
    -------
    int
        Indeks kemunculan pattern pada text, jika tidak ada -1

    Example
    -------
    >>> boyer_moore(pattern='a', text='bcda')
    3
    >>> boyer_moore(pattern='a', text='bcd')
    -1
    '''
    last_occurance = find_last_occurance(pattern)
    pjg_pat = len(pattern)
    pjg_text = len(text)

    # Kalau panjang text lebih sedikit dari pattern, otomatis tidak sama
    if pjg_text < pjg_pat:
        return -1

    i = pjg_pat - 1  # iterator pattern
    j = i  # iterator text
    count = 0
    while j < pjg_text:
        count += 1
        if text[j] == pattern[i]:
            if i == 0:
                return j

            j -= 1
            i -= 1

        else:
            jump_idx = last_occurance[text[j]]
            i = pjg_pat - 1
            j += pjg_pat - min(j, 1 + jump_idx)

    return -1


if __name__ == '__main__':
    text = 'HERE IS A SIMPLE EXAMPLE'
    idx = boyer_moore(text=text, pattern='EXAMPLE')
    print(idx)
    print(text[idx:])
