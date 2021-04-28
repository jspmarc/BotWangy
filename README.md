# Bot Wangy

# General Info
Deadline reminder assistant dalam bentuk chatbot
Menerapkan string matching dan regular expression

## Cara deploy:
1. `cd src/view`
2. `npm install`
2. `npm run build`
3. `cd ..`
4. `pipenv install`
5. `pipenv run flask run`

## Development dengan auto-update/live-update:
Pada sebuah terminal, jalankan:
1. `cd src`
2. `pipenv install` (jika belum pernah melakukan ini pada project ini)
3. `pipenv shell`
4. `python3 app.py`

Pada terminal lain, jalankan:
1. `cd src/view`
2. `npm install` (jika belum pernah melakukan ini pada project ini)
3. `npm run dev`

Sekarang perubahan pada file `app.py` ataupun file Svelte akan otomatis berubah.

## Dependencies
1. Python 3.9 and pipenv

   Digunakan u/ backend. Dependencies python dapat dilihat pada
   [src/Pipfile](src/Pipfile). Dependencies akan otomatis diinstall oleh
   pipenv.

2. Node.js

   Digunakan untuk frontend (Svelte). Dependencies dapat dilihat pada
   [src/view/package.json](src/view/package.json). Dependencies akan otomatis
   diinstall oleh Node.js.

## Features
1. Menambahkan tugas baru
2. Melihat daftar tugas yang dikerjakan
3. Menampilkan deadline dari suatu tugas tertentu
4. Memperbarui deadline tugas tertentu
5. Menandai suatu tugas sudah selesai dikerjakan
6. Menampilkan opsi help yang difasilitasi oleh assistant
7. Merekomendasikan kata ketika pengguna melakukan saltik

## Status
Finished

### Credits:
| nama | NIM |
|------|-----|
| Reinaldo Antolis | 13519015 |
| Jeane Mikha E. | 13519116 |
| Josep Marcello | 13519164 |
