# Pengujian — Dikerjakan Bersama

Pengujian dikerjakan **semua anggota**. Setiap anggota menguji bagian yang dibuatnya sendiri.

| Anggota | Yang diuji |
|---|---|
| 1 — Fungsi keanggotaan | Nilai di titik batas, tidak ada celah input |
| 2 — Basis aturan | Semua input mengaktifkan aturan, data kontradiktif |
| 3 — Mamdani | Validasi manual vs program, sensitivitas |
| 4 — Web | Input lewat web, data ekstrem |
| Semua | 24 data simulasi, uji otomatis, keterbatasan |

Uji otomatis: `python test_fuzzy.py` → **12 uji, semua lulus**.

---

## 1. Data uji (24 mahasiswa) — semua anggota

| Jenis | Tujuan | Penanggung jawab |
|---|---|---|
| Ekstrem | Apakah nilai terbaik/terburuk menghasilkan skor tertinggi/terendah? | Anggota 4 |
| Titik batas | Apakah sistem tetap jalan tepat di batas kategori? | Anggota 1 |
| Tumpang tindih | Apakah banyak aturan aktif bersamaan? | Anggota 3 |
| Kontradiktif | Apakah hasilnya masuk akal saat kriteria saling bertentangan? | Anggota 2 |
| Umum | Gambaran pemakaian nyata | Semua |

Hasil penting:

| Mahasiswa | Kondisi | Hasil | Masuk akal? |
|---|---|---|---|
| M01 | Semua terbaik | **Sangat layak** | ✅ Tertinggi |
| M02 | Semua terburuk | **Tidak layak** | ✅ Terendah |
| M12 | IPK tinggi, orang tua kaya | Cukup layak | ✅ Pintar tapi tidak butuh bantuan |
| M13 | IPK rendah, miskin, prestasi tinggi | Layak | ✅ Kebutuhan dan prestasi menolong |
| M15 | IPK rendah, orang tua kaya | Tidak layak | ✅ Prestasi tinggi tidak cukup menutupi |
| M16 | IPK tinggi, miskin, tanggungan banyak | **Sangat layak** | ✅ Calon ideal |

Semua 24 data berhasil diproses tanpa error.

## 2. Titik batas & celah — Anggota 1

- Nilai **tepat di batas** (misalnya IPK 2,5 / 3,0 / 3,5) diproses tanpa error.
- Di setiap titik, jumlah derajat kategori yang bersebelahan **selalu 1**, jadi tidak ada nilai yang tidak terwakili.

## 3. Cakupan aturan — Anggota 2

- Program mencoba **ratusan ribu kombinasi input**.
- Hasilnya: **tidak ada satu pun** kombinasi yang tidak mengaktifkan aturan.

## 4. Validasi manual — Anggota 3

Hitungan manual ditulis **terpisah** dari program, lalu hasilnya dibandingkan:

| Mahasiswa | Program | Manual | Kesimpulan |
|---|---|---|---|
| M01 | 87,0 | 86,8 | Sama |
| M05 | 40,0 | 40,0 | Sama persis |
| M10 | 53,8 | 53,7 | Sama |
| M12 | 40,0 | 40,0 | Sama persis |
| M16 | 79,9 | 79,7 | Sama |

Selisihnya **di bawah 0,2 poin**, hanya karena beda kehalusan langkah hitung. **Program terbukti benar.**

## 5. Sensitivitas — Anggota 3

Satu input diubah, tiga lainnya tetap:

| Input dinaikkan | Skor | Wajar? |
|---|---|---|
| IPK ↑ | naik (sekitar 13 → 65) | ✅ |
| Penghasilan ↑ | **turun** (sekitar 73 → 25) | ✅ Makin kaya, makin kurang butuh |
| Tanggungan ↑ | naik (sekitar 40 → 65) | ✅ |
| Prestasi ↑ | naik (sekitar 40 → 65) | ✅ |

Pola yang terlihat:

- **Bagian datar:** nilai sudah pasti di satu kategori, jadi skor tidak berubah.
- **Bagian naik/turun bertahap:** nilai berada di antara dua kategori. Inilah kelebihan fuzzy: perubahannya halus, tidak melompat.
- **IPK dan penghasilan paling berpengaruh**, karena bobotnya paling besar.
- Ada sedikit penurunan (**kurang dari 1 poin**) di beberapa titik. Ini sifat bawaan Mamdani, bukan kesalahan program.

## 6. Uji web — Anggota 4

| Uji | Hasil |
|---|---|
| Halaman dibuka | Tidak ada error, 5 tab tampil |
| Input nilai terbaik | Sangat layak ✅ |
| Input nilai terburuk | Tidak layak ✅ |
| Slider dan kotak ketik | Sinkron ✅ |
| Nilai di luar batas | Ditolak ✅ |

## 7. Keterbatasan — semua anggota

| Keterbatasan | Terkait |
|---|---|
| Batas kategori (misalnya “IPK tinggi mulai 3,0”) ditentukan sendiri oleh kelompok | Anggota 1 |
| Bobot aturan (IPK & penghasilan paling penting) adalah pilihan kelompok | Anggota 2 |
| Skor tidak pernah 0 atau 100 karena sifat centroid | Anggota 3 |
| Data yang dipakai simulasi, bukan data mahasiswa asli | Semua |
| Hasil hanya rekomendasi, keputusan akhir di panitia | Semua |

---

## Persiapan tanya jawab (bisa ditanyakan ke siapa saja)

**T: Bagaimana kalian tahu program sudah benar?**
J: Hasil program dicocokkan dengan hitungan manual pada 5 mahasiswa, dan hasilnya hampir sama. Selain itu ada 12 uji otomatis yang semuanya lulus.

**T: Apa itu data kontradiktif?**
J: Data dengan kriteria yang saling bertolak belakang, misalnya pintar tapi orang tuanya kaya. Gunanya menguji apakah sistem menimbang kriteria dengan adil.

**T: Apa kesimpulan analisis sensitivitas?**
J: Arah perubahan skor sudah sesuai logika, perubahannya halus, dan IPK serta penghasilan paling berpengaruh.
