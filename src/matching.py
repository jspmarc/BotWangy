'''
Module yang mengandung fungsi matching

Reinaldo Antolis / 13519015
Jeane Mikha / 13519116
Josep Marcello / 13519164

24 April 2021
'''
import string


def find_last_occurance(s: str) -> 'dict[str, int]':
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


def boyer_moore(text: str, pattern: str) -> int:
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


def levenshtein_distance(s1: str, s2: str, i: int, j: int) -> int:
    '''
    Fungsi untuk menghitung jarak levenshtein antara 2 string.

    Parameters
    ----------
    s1 : str
        string pertama
    s2 : str
        string kedua
    i : int
        karakter ke-i pada s1 (dimulai dari 1)
    j : int
        karakter ke-j pada s2 (dimulai dari 1)

    Returns
    -------
    int
        Jarak levenshtein kedua string

    Example
    -------
    >>> boyer_moore(s1='kitten', s2='sitting')
    3
    '''
    if i == 0 or j == 0:
        return max(i, j)

    s1 = '\0' + s1 if s1[0] != '\0' else s1
    s2 = '\0' + s2 if s2[0] != '\0' else s2
    ret = [[0 for _ in s2] for _ in s1]

    return ret[-1][-1]


if __name__ == '__main__':
    text = 'HERE IS A SIMPLE EXAMPLE'
    idx = boyer_moore(text=text, pattern='EXAMPLE')
    print(idx)
    print(levenshtein_distance(s1='kitten', i=1, s2='sitting', j=1))
