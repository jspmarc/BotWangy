-- DROP TABLE IF EXISTS matkul;
-- CREATE TABLE matkul (
--     id_matkul VARCHAR(6) PRIMARY KEY,
--     nama_matkul TEXT NOT NULL
-- );

DROP TABLE IF EXISTS tugas;
CREATE TABLE tugas (
    id_tugas INT PRIMARY KEY AUTO_INCREMENT,
    topik_tugas TEXT NOT NULL,
    jenis_tugas ENUM('tubes', 'tucil', 'praktikum', 'kuis', 'ujian', 'tugas') NOT NULL,
    deadline_tugas DATETIME NOT NULL,
    id_matkul VARCHAR(6) NOT NULL,
    FOREIGN KEY(id_matkul) REFERENCES matkul(id_matkul)
);

DROP TABLE IF EXISTS tugas_akan_datang;
CREATE TABLE tugas_akan_datang (
    id_tugas INT PRIMARY KEY AUTO_INCREMENT,
    FOREIGN KEY(id_tugas) REFERENCES tugas(id_tugas)
);
