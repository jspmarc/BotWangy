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
    while j < pjg_text:
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


def levenshtein_distance(s1: str, s2: str) -> int:
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
    >>> levenshtein_distance(s1='kitten', i=0, s2='sitting', j=0)
    3
    '''
    s1 = '\0' + s1
    s2 = '\0' + s2
    len_s1 = len(s1)
    len_s2 = len(s2)
    ret = [[None for _ in s2] for _ in s1]

    def fill(i: int, j: int):
        if min(i, j) == 0:
            return max(i, j)
        if ret[i][j] is not None:
            return ret[i][j]

        case_1 = fill(i - 1, j) + 1
        case_2 = fill(i, j - 1) + 1
        case_3 = fill(i - 1, j - 1) +\
            (1 if s1[i] != s2[j] else 0)

        return min(case_1, case_2, case_3)

    s1_idx = 1
    while s1_idx < len_s1:
        s2_idx = 1
        while s2_idx < len_s2:
            ret[s1_idx][s2_idx] = fill(s1_idx, s2_idx)
            s2_idx += 1
        s1_idx += 1

    return ret[-1][-1]


if __name__ == '__main__':
    print(levenshtein_distance(s1='sitting', s2='kitten'))
