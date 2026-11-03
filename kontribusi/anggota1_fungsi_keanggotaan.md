# Anggota 1 — Analis Masalah & Fungsi Keanggotaan

**Nama:** [Nama]

## Apa yang saya kerjakan

1. Menjelaskan **masalah, tujuan, dan pengguna** sistem.
2. Menentukan **5 variabel** (4 input + 1 output) beserta kategorinya.
3. Merancang **fungsi keanggotaan**, yaitu grafik yang mengubah angka menjadi “rendah/sedang/tinggi”.
4. Memastikan **tidak ada nilai input yang tidak terwakili**.

Bagian kode: `VAR` dan `mu()` di `fuzzy_beasiswa.py`. Grafiknya bisa dilihat di tab **Fungsi keanggotaan** pada web.

---

## 1. Masalah yang diselesaikan

Kalau aturan seleksi kaku, misalnya “IPK minimal 3,0”, mahasiswa dengan IPK **2,99 langsung gugur**, padahal bedanya hanya sedikit.

Logika fuzzy menyelesaikan ini: IPK 2,99 dianggap **“hampir sedang”**, tidak langsung dicoret.

- **Tujuan:** membantu panitia menilai kelayakan beasiswa dengan adil dan konsisten.
- **Pengguna:** panitia seleksi beasiswa.
- **Skor:** 0–100. Makin tinggi makin layak. Skor ini **rekomendasi**, keputusan akhir tetap di panitia.

## 2. Variabel

| Variabel | Rentang | Kategori |
|---|---|---|
| IPK | 0 – 4 | Rendah, Sedang, Tinggi |
| Penghasilan orang tua | Rp 0 – 15 juta | Rendah, Sedang, Tinggi |
| Jumlah tanggungan | 0 – 8 orang | Sedikit, Sedang, Banyak |
| Prestasi | 0 – 100 | Rendah, Sedang, Tinggi |
| **Kelayakan (output)** | 0 – 100 | Tidak layak, Cukup layak, Layak, Sangat layak |

## 3. Fungsi keanggotaan (dijelaskan dengan mudah)

Fungsi keanggotaan menjawab pertanyaan: **“seberapa besar nilai ini termasuk kategori X?”** Jawabannya berupa angka dari 0 (bukan) sampai 1 (pasti).

Contoh untuk **IPK**:

| IPK | Rendah | Sedang | Tinggi | Artinya |
|---|---|---|---|---|
| 2,0 | 1 | 0 | 0 | Pasti rendah |
| 2,75 | ½ | ½ | 0 | Setengah rendah, setengah sedang |
| 3,0 | 0 | 1 | 0 | Pasti sedang |
| 3,25 | 0 | ½ | ½ | Setengah sedang, setengah tinggi |
| 3,8 | 0 | 0 | 1 | Pasti tinggi |

Batas kategori setiap input:

| Variabel | Pasti rendah/sedikit | Pasti sedang | Pasti tinggi/banyak |
|---|---|---|---|
| IPK | ≤ 2,5 | tepat 3,0 | ≥ 3,5 |
| Penghasilan | ≤ Rp 2 jt | Rp 5 – 7 jt | ≥ Rp 10 jt |
| Tanggungan | ≤ 1 orang | 3 – 4 orang | ≥ 6 orang |
| Prestasi | ≤ 30 | 50 – 60 | ≥ 80 |

Di antara batas-batas itu, nilainya berpindah kategori **sedikit demi sedikit** (garis miring pada grafik).

## 4. Alasan memilih bentuk grafik

- **Trapesium di ujung kiri dan kanan:** nilai ekstrem seperti IPK 4,0 atau 3,6 sama-sama pasti “tinggi”, jadi grafiknya datar di angka 1.
- **Trapesium di tengah** (penghasilan, tanggungan, prestasi): ada **rentang** nilai yang sama-sama dianggap sedang, misalnya 3 maupun 4 orang tanggungan.
- **Segitiga di tengah** (IPK): hanya ada satu titik paling sedang, yaitu 3,0.
- **Garis lurus:** mudah dihitung manual dan mudah diperiksa.

## 5. Kenapa tidak ada celah

Kategori yang bersebelahan dibuat **saling melengkapi**: jumlahnya selalu 1. Di titik pertemuannya masing-masing bernilai ½.

Akibatnya, **setiap nilai input pasti punya kategori dengan derajat minimal ½**, sehingga tidak ada nilai yang “tidak dikenali” sistem.

Desain ini juga hasil perbaikan. Versi awal hanya bertemu di derajat ¼, sehingga skor kadang turun padahal kriteria mahasiswa membaik.

## 6. Bagian pengujian saya

- Menguji nilai **tepat di titik batas** (misalnya IPK 2,5 / 3,0 / 3,5): semuanya diproses tanpa error.
- Memastikan jumlah derajat kategori bersebelahan **selalu 1** di sepanjang rentang input.
- Menulis keterbatasan: batas kategori bersifat **subjektif**.

Detailnya ada di [pengujian_bersama.md](pengujian_bersama.md).

---

## Persiapan tanya jawab

**T: Kenapa pakai fuzzy, bukan batas tegas?**
J: Supaya perbedaan kecil (IPK 2,99 vs 3,0) tidak membuat hasil berubah drastis.

**T: Dari mana angka batas, misalnya IPK tinggi mulai 3,0?**
J: Ditentukan oleh kelompok berdasarkan kebiasaan umum seleksi beasiswa. Ini subjektif, dan sudah kami tulis sebagai keterbatasan.

**T: Apa arti derajat 0,5?**
J: Nilai itu setengah termasuk kategori tersebut, karena berada tepat di perbatasan dua kategori.

**T: Kenapa penghasilan “rendah” justru baik?**
J: Beasiswa ditujukan untuk yang membutuhkan, jadi penghasilan rendah menaikkan kelayakan.
