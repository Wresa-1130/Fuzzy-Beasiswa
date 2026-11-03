# SPK Kelayakan Penerima Beasiswa — Logika Fuzzy Mamdani

Penjelasan sistem beserta pembuktian bahwa perhitungannya benar.

**Menjalankan**

```bash
pip install -r requirements.txt
streamlit run app.py          # web
python fuzzy_beasiswa.py      # semua pengujian + grafik/CSV ke folder hasil_fuzzy/
python test_fuzzy.py          # 12 uji otomatis
python fuzzy_beasiswa.py --ipk 3.25 --peng 8 --tang 5 --pres 70   # satu mahasiswa
```

| Berkas | Isi |
|---|---|
| `fuzzy_beasiswa.py` | Mesin fuzzy: fungsi keanggotaan, 81 aturan, inferensi Mamdani, data uji, validasi, sensitivitas |
| `app.py` | Web Streamlit (5 tab) |
| `test_fuzzy.py` | Uji otomatis |

---

## 1. Identifikasi masalah

- **Masalah:** seleksi beasiswa melibatkan kriteria yang samar (“IPK cukup tinggi”, “penghasilan agak rendah”). Batas tegas (mis. IPK ≥ 3,0) membuat mahasiswa IPK 2,99 langsung gugur.
- **Tujuan:** memberi skor kelayakan 0–100 yang konsisten dan dapat ditelusuri.
- **Pengguna:** panitia / admin seleksi beasiswa.
- **Makna skor:** makin tinggi makin layak. Skor adalah **rekomendasi pendukung keputusan**, keputusan akhir tetap di tangan panitia.

| Skor | Rekomendasi |
|---|---|
| < 27,5 | Tidak layak |
| 27,5 – < 52,5 | Cukup layak |
| 52,5 – < 75 | Layak |
| ≥ 75 | Sangat layak |

Batas ini adalah titik potong himpunan output (lihat §2.5), bukan angka sembarang.

---

## 2. Variabel & fungsi keanggotaan

Notasi: `trap(a,b,c,d)` naik dari a ke b, bernilai 1 dari b ke c, turun dari c ke d.
`tri(a,b,c)` = `trap(a,b,b,c)`.

$$
\mu_{trap}(x)=\begin{cases}
0 & x<a \text{ atau } x>d\\
\dfrac{x-a}{b-a} & a\le x<b\\
1 & b\le x\le c\\
\dfrac{d-x}{d-c} & c<x\le d
\end{cases}
$$

### Alasan pemilihan bentuk

- **Trapesium bahu** di ujung semesta: nilai ekstrem (mis. IPK 3,5–4) sudah pasti “Tinggi”, jadi derajat tetap 1.
- **Trapesium** untuk “Sedang” pada Penghasilan, Tanggungan, Prestasi: ada *rentang* nilai yang sama-sama dianggap sedang (mis. 3–4 orang).
- **Segitiga** untuk IPK Sedang: hanya satu nilai paling “sedang” (3,0).
- **Partisi Ruspini** untuk semua input: himpunan bertetangga selalu berjumlah 1 dan berpotongan di μ = 0,5. Akibatnya tidak ada celah, dan perubahan input menghasilkan perubahan skor yang halus.
- **Linear** dipilih karena mudah dihitung manual dan diperiksa.

### 2.1 IPK (0–4)

| Himpunan | Parameter | Persamaan |
|---|---|---|
| Rendah | trap(0, 0, 2.5, 3) | 1 jika x ≤ 2,5; (3 − x)/0,5 jika 2,5 < x ≤ 3 |
| Sedang | tri(2.5, 3, 3.5) | (x − 2,5)/0,5 jika 2,5 ≤ x < 3; (3,5 − x)/0,5 jika 3 ≤ x ≤ 3,5 |
| Tinggi | trap(3, 3.5, 4, 4) | (x − 3)/0,5 jika 3 ≤ x < 3,5; 1 jika x ≥ 3,5 |

### 2.2 Penghasilan orang tua (Rp 0–15 juta/bulan)

| Himpunan | Parameter | Persamaan |
|---|---|---|
| Rendah | trap(0, 0, 2, 5) | 1 jika x ≤ 2; (5 − x)/3 jika 2 < x ≤ 5 |
| Sedang | trap(2, 5, 7, 10) | (x − 2)/3; 1 pada 5–7; (10 − x)/3 |
| Tinggi | trap(7, 10, 15, 15) | (x − 7)/3 jika 7 ≤ x < 10; 1 jika x ≥ 10 |

### 2.3 Jumlah tanggungan (0–8 orang)

| Himpunan | Parameter | Persamaan |
|---|---|---|
| Sedikit | trap(0, 0, 1, 3) | 1 jika x ≤ 1; (3 − x)/2 jika 1 < x ≤ 3 |
| Sedang | trap(1, 3, 4, 6) | (x − 1)/2; 1 pada 3–4; (6 − x)/2 |
| Banyak | trap(4, 6, 8, 8) | (x − 4)/2 jika 4 ≤ x < 6; 1 jika x ≥ 6 |

### 2.4 Prestasi (skor 0–100)

| Himpunan | Parameter | Persamaan |
|---|---|---|
| Rendah | trap(0, 0, 30, 50) | 1 jika x ≤ 30; (50 − x)/20 jika 30 < x ≤ 50 |
| Sedang | trap(30, 50, 60, 80) | (x − 30)/20; 1 pada 50–60; (80 − x)/20 |
| Tinggi | trap(60, 80, 100, 100) | (x − 60)/20 jika 60 ≤ x < 80; 1 jika x ≥ 80 |

### 2.5 Output: Kelayakan (0–100)

| Himpunan | Parameter |
|---|---|
| Tidak layak | trap(0, 0, 15, 35) |
| Cukup layak | tri(20, 40, 60) |
| Layak | tri(45, 65, 85) |
| Sangat layak | trap(65, 85, 100, 100) |

Titik potong (dasar batas label): (35 − z)/20 = (z − 20)/20 → **z = 27,5**; begitu juga **52,5** dan **75**.

### 2.6 Bukti tidak ada celah input

- **Per variabel:** pada 2.001 titik tiap semesta, jumlah derajat input = 1 tepat, dan derajat terbesar ≥ 0,5 (`test_partisi_ruspini_dan_tanpa_celah`).
- **Gabungan 4 input:** 453.747 kombinasi diperiksa (`cek_coverage()`): **0** kombinasi tanpa aturan aktif, α terkuat di titik terlemah = **0,50**.

Grafik semua fungsi ada di tab **Fungsi keanggotaan** (garis hitam = input saat ini) dan file `hasil_fuzzy/mf_*.png`.

---

## 3. Basis aturan

Faktorial lengkap **3 × 3 × 3 × 3 = 81 aturan**; setiap aturan memakai keempat input.

Konsekuen ditentukan dengan sistem poin agar konsisten dan bisa diperiksa:

| Kategori → poin | 0 | 1 | 2 | Bobot |
|---|---|---|---|---|
| IPK | Rendah | Sedang | Tinggi | ×3 |
| Penghasilan | Tinggi | Sedang | Rendah | ×3 |
| Tanggungan | Sedikit | Sedang | Banyak | ×2 |
| Prestasi | Rendah | Sedang | Tinggi | ×2 |

Total 0–20 → **≤ 7** Tidak layak · **8–11** Cukup layak · **12–15** Layak · **≥ 16** Sangat layak.
IPK dan penghasilan diberi bobot lebih besar karena merupakan kriteria utama (prestasi akademik dan kebutuhan ekonomi).

Contoh aturan:

| No | IF IPK | AND Penghasilan | AND Tanggungan | AND Prestasi | Poin | THEN |
|---|---|---|---|---|---|---|
| R1 | Rendah | Tinggi | Sedikit | Rendah | 0 | Tidak layak |
| R27 | Rendah | Rendah | Banyak | Tinggi | 14 | Layak |
| R41 | Sedang | Sedang | Sedang | Sedang | 10 | Cukup layak |
| R55 | Tinggi | Tinggi | Sedikit | Rendah | 6 | Tidak layak |
| R81 | Tinggi | Rendah | Banyak | Tinggi | 20 | Sangat layak |

Sebaran: Tidak layak 23 · Cukup layak 28 · Layak 22 · Sangat layak 8. Daftar lengkap ada di tab **Basis aturan** dan `hasil_fuzzy/aturan_fuzzy.csv`.

**Mengapa 81, bukan 15?** Tugas menegaskan jumlah minimal tidak menjamin cakupan. Dengan semua kombinasi kategori punya aturan, dan setiap input punya derajat ≥ 0,5 di minimal satu kategori, **pasti** ada aturan dengan α ≥ 0,5 untuk setiap input valid.

---

## 4. Inferensi Mamdani

| Tahap | Operasi | Kode (`fuzzy_beasiswa.py`) |
|---|---|---|
| Fuzzifikasi | μ tiap himpunan | `fuzzifikasi()` |
| α-predikat | **AND = MIN** | `alpha_aturan()` |
| Implikasi | **MIN**: μᵢ(z) = min(αᵢ, μ_out(z)) | `np.minimum(a, OUT_MU[...])` |
| Agregasi | **MAX** atas 81 aturan | `np.maximum(agg, ...)` |
| Defuzzifikasi | **Centroid diskrit** z* = Σ z·μ(z) / Σ μ(z) | `infer()` |

**Grid output:** z = 0; 0,5; 1,0; …; 100 → **201 titik, interval 0,5**.

---

## 5. Contoh perhitungan lengkap — M10

Input: **IPK 3,25 · Penghasilan Rp 8 juta · Tanggungan 5 · Prestasi 70**

### 5.1 Fuzzifikasi

| Variabel | Perhitungan | Hasil |
|---|---|---|
| IPK Sedang | (3,5 − 3,25)/0,5 | 0,5 |
| IPK Tinggi | (3,25 − 3)/0,5 | 0,5 |
| Penghasilan Sedang | (10 − 8)/3 | 0,667 |
| Penghasilan Tinggi | (8 − 7)/3 | 0,333 |
| Tanggungan Sedang | (6 − 5)/2 | 0,5 |
| Tanggungan Banyak | (5 − 4)/2 | 0,5 |
| Prestasi Sedang | (80 − 70)/20 | 0,5 |
| Prestasi Tinggi | (70 − 60)/20 | 0,5 |

Himpunan lain = 0. Aturan aktif = 2 × 2 × 2 × 2 = **16**.

### 5.2 α-predikat (MIN)

| Aturan | IPK | Peng. | Tang. | Pres. | Poin | Output | α |
|---|---|---|---|---|---|---|---|
| R32 | S | T | S | S | 7 | Tidak layak | min(.5, .333, .5, .5) = **0,333** |
| R33 | S | T | S | T | 9 | Cukup layak | 0,333 |
| R35 | S | T | B | S | 9 | Cukup layak | 0,333 |
| R36 | S | T | B | T | 11 | Cukup layak | 0,333 |
| R41 | S | S | S | S | 10 | Cukup layak | min(.5, .667, .5, .5) = **0,5** |
| R42 | S | S | S | T | 12 | Layak | 0,5 |
| R44 | S | S | B | S | 12 | Layak | 0,5 |
| R45 | S | S | B | T | 14 | Layak | 0,5 |
| R59 | T | T | S | S | 10 | Cukup layak | 0,333 |
| R60 | T | T | S | T | 12 | Layak | 0,333 |
| R62 | T | T | B | S | 12 | Layak | 0,333 |
| R63 | T | T | B | T | 14 | Layak | 0,333 |
| R68 | T | S | S | S | 13 | Layak | 0,5 |
| R69 | T | S | S | T | 15 | Layak | 0,5 |
| R71 | T | S | B | S | 15 | Layak | 0,5 |
| R72 | T | S | B | T | 17 | Sangat layak | **0,5** |

### 5.3 Implikasi (MIN) — tinggi potong tiap output

Untuk output yang sama, potongan tertinggi yang menentukan (karena agregasi MAX):

| Output | α maks | Dari |
|---|---|---|
| Tidak layak | 0,333 | R32 |
| Cukup layak | 0,5 | R41 |
| Layak | 0,5 | R42, R44, … |
| Sangat layak | 0,5 | R72 |

### 5.4 Agregasi (MAX)

Gabungan keempat potongan menghasilkan kurva μ(z):

| Rentang z | μ(z) | Sumber |
|---|---|---|
| 0 – 26,67 | 1/3 | Tidak layak terpotong 1/3 |
| 26,67 – 30 | (z − 20)/20 | Kaki naik Cukup layak |
| 30 – 50 | 0,5 | Cukup layak terpotong 0,5 |
| 50 – 52,5 | (60 − z)/20 | Kaki turun Cukup layak |
| 52,5 – 55 | (z − 45)/20 | Kaki naik Layak (lembah μ = 0,375 di 52,5) |
| 55 – 100 | 0,5 | Layak lalu Sangat layak, sama-sama 0,5 |

### 5.5 Defuzzifikasi centroid

**a. Perhitungan tangan (integral eksak per segmen)**

| Segmen | Luas ∫μ dz | Momen ∫z·μ dz |
|---|---|---|
| 0 – 26,67 | 8,8889 | 118,5185 |
| 26,67 – 30 | 1,3889 | 39,5062 |
| 30 – 50 | 10,0000 | 400,0000 |
| 50 – 52,5 | 1,0938 | 55,9896 |
| 52,5 – 55 | 1,0938 | 58,8542 |
| 55 – 100 | 22,5000 | 1743,7500 |
| **Total** | **44,9653** | **2416,6184** |

z* = 2416,6184 / 44,9653 = **53,74**

**b. Program (grid diskrit 0,5)**

Σ μ(z) = 90,350 · Σ z·μ(z) = 4858,325 → z* = 4858,325 / 90,350 = **53,77**

Selisih 0,03 hanya karena resolusi grid.

**c. Label:** di z = 53,77 → μ Cukup layak = (60 − 53,77)/20 = 0,31; μ Layak = (53,77 − 45)/20 = 0,44 → **Layak**.

Angka-angka ini dikunci oleh `test_contoh_m10_sesuai_hitungan_tangan`. Tahap yang sama tampil di tab **Hasil** web untuk input apa pun.

---

## 6. Pengujian 24 data

| ID | IPK | Peng. | Tang. | Pres. | Jenis uji | Skor | Rekomendasi |
|---|---|---|---|---|---|---|---|
| M01 | 4.00 | 0.0 | 8 | 100 | Ekstrem | 86.97 | Sangat layak |
| M02 | 0.00 | 15.0 | 0 | 0 | Ekstrem | 13.03 | Tidak layak |
| M03 | 4.00 | 15.0 | 0 | 100 | Ekstrem | 40.00 | Cukup layak |
| M04 | 0.00 | 0.0 | 8 | 0 | Ekstrem | 40.00 | Cukup layak |
| M05 | 3.00 | 5.0 | 3 | 50 | Titik batas | 40.00 | Cukup layak |
| M06 | 2.50 | 2.0 | 1 | 30 | Titik batas | 13.03 | Tidak layak |
| M07 | 3.50 | 10.0 | 6 | 80 | Titik batas | 65.00 | Layak |
| M08 | 2.75 | 3.5 | 2 | 40 | Titik batas | 39.93 | Cukup layak |
| M09 | 2.75 | 4.0 | 5 | 40 | Tumpang tindih | 39.93 | Cukup layak |
| M10 | 3.25 | 8.0 | 5 | 70 | Tumpang tindih | 53.77 | Layak |
| M11 | 3.10 | 6.5 | 3.5 | 55 | Tumpang tindih | 46.30 | Cukup layak |
| M12 | 3.90 | 14.0 | 1 | 90 | Kontradiktif | 40.00 | Cukup layak |
| M13 | 2.10 | 1.0 | 7 | 85 | Kontradiktif | 65.00 | Layak |
| M14 | 3.80 | 1.5 | 0 | 10 | Kontradiktif | 65.00 | Layak |
| M15 | 2.00 | 12.0 | 2 | 95 | Kontradiktif | 15.01 | Tidak layak |
| M16 | 3.70 | 2.5 | 5 | 75 | Umum | 79.87 | Sangat layak |
| M17 | 3.40 | 4.5 | 4 | 60 | Umum | 62.15 | Layak |
| M18 | 3.00 | 7.0 | 3 | 45 | Umum | 40.00 | Cukup layak |
| M19 | 2.60 | 9.0 | 2 | 35 | Umum | 22.59 | Tidak layak |
| M20 | 3.60 | 11.0 | 5 | 65 | Umum | 52.50 | Layak |
| M21 | 2.90 | 3.5 | 6 | 70 | Umum | 68.31 | Layak |
| M22 | 3.20 | 5.5 | 7 | 20 | Umum | 50.63 | Cukup layak |
| M23 | 4.00 | 7.0 | 4 | 60 | Titik batas | 65.00 | Layak |
| M24 | 3.00 | 15.0 | 8 | 100 | Titik batas | 40.00 | Cukup layak |

**Pembacaan hasil (bukti kewajaran):**

- **Ekstrem:** profil terbaik (M01) tertinggi, terburuk (M02) terendah. Profil campuran (M03, M04) berada di tengah — sesuai, karena akademik dan ekonomi saling mengimbangi.
- **Titik batas:** input tepat di batas tidak error dan selalu ada aturan aktif. Di titik silang μ = 0,5 (M08) 16 aturan aktif sekaligus.
- **Tumpang tindih:** banyak aturan aktif (M09, M10: 16 aturan) → skor merupakan perpaduan beberapa kategori.
- **Kontradiktif:** M12 (pintar tapi mampu) hanya Cukup layak; M14 (IPK tinggi, miskin, prestasi rendah) Layak; M15 (IPK rendah, mampu) Tidak layak meski prestasinya 95. Sesuai bobot IPK dan penghasilan yang lebih besar.
- **Rentang skor 13,03 – 86,97:** bukan 0–100 karena centroid adalah titik berat luas — tidak bisa mencapai ujung semesta. Ini sifat normal centroid.

---

## 7. Validasi program vs manual

“Manual” = fungsi `hitung_manual()` yang ditulis ulang terpisah (fungsi segitiga/trapesium sendiri, loop biasa, langkah centroid 0,01).

| ID | Program (grid 0,5) | Manual (langkah 0,01) | Selisih |
|---|---|---|---|
| M01 | 86,9653 | 86,8360 | 0,1294 |
| M05 | 40,0000 | 40,0000 | 0,0000 |
| M10 | 53,7723 | 53,7447 | 0,0276 |
| M12 | 40,0000 | 40,0000 | 0,0000 |
| M16 | 79,8747 | 79,7376 | 0,1371 |

Cek tangan tambahan:
- **M10:** integral eksak = 53,7441 (§5.5).
- **M01:** hanya “Sangat layak” α = 1 aktif → centroid trapesium (65, 85, 100, 100):
  luas = 10 + 15 = 25; momen = 783,33 + 1387,5 = 2170,83 → z* = **86,83**. Cocok.
- **M05:** hanya R41 aktif (α = 1) → Cukup layak utuh, segitiga simetris di 40 → z* = **40**. Cocok.

Semua selisih < 0,14 poin dan hanya berasal dari resolusi grid. Program terbukti menghitung Mamdani dengan benar. Selain itu `test_operator_mamdani_dihitung_ulang` menghitung ulang MIN–MIN–MAX–centroid untuk 24 data dan hasilnya identik.

---

## 8. Analisis sensitivitas

Nilai dasar: IPK 3,2 · Penghasilan 6 · Tanggungan 4 · Prestasi 60. Satu input diubah, lainnya tetap.

| Input diubah | Pola skor |
|---|---|
| IPK 0 → 4 | 13,03 datar (≤ 2,5) → naik tajam 2,5–3,5 (27,45 → 40 → 52,5 → 65) → datar 65 |
| Penghasilan 0 → 15 | 73,01 datar (≤ 2) → turun 2–5 → datar 50,63 (5–7) → turun 7–10 → datar 25,08 |
| Tanggungan 0 → 8 | 40 (≤ 1) → 51,4 (2) → 50,63 (3–4) → 52,5 (5) → 65 (≥ 6) |
| Prestasi 0 → 100 | 40 (≤ 30) → 51,4 (40) → 50,63 (50–60) → 52,5 (70) → 65 (≥ 80) |

**Penjelasan pola:**

1. **Arah sesuai logika:** IPK, tanggungan, prestasi naik → skor naik; penghasilan naik → skor turun.
2. **Daerah datar** terjadi saat input berada di inti satu himpunan (μ = 1): kategori tidak berubah, maka skor tidak berubah.
3. **Daerah miring** terjadi di daerah tumpang tindih — di situlah fuzzy “menghaluskan” perpindahan kategori, bukan melompat seperti aturan tegas.
4. **IPK dan penghasilan paling sensitif** (rentang perubahan ±50 poin) karena bobotnya ×3; tanggungan dan prestasi (×2) ±25 poin.
5. **Penurunan kecil 51,4 → 50,63** (tanggungan 2 → 3, prestasi 40 → 50) adalah sifat bawaan Mamdani MIN–MAX:
   di tanggungan = 2, aturan “IPK Sedang” dibatasi μ tanggungan 0,5; di tanggungan = 3 batas itu hilang sehingga potongan *Cukup layak* naik ke 0,6 sementara *Layak* tetap 0,4 → centroid bergeser sedikit ke kiri.
   Diuji pada ±106.000 titik: penurunan seperti ini **selalu < 1 poin** (`test_arah_pengaruh_input`), dan arah ujung-ke-ujung selalu benar.

Grafik ada di tab **Validasi & sensitivitas** dan `hasil_fuzzy/sensitivitas.png`.

---

## 9. Keterbatasan

- **Subjektivitas parameter:** batas seperti “IPK tinggi mulai 3,0” atau “penghasilan rendah ≤ Rp 2 juta” ditentukan perancang, bukan dari data nyata. Parameter berbeda → skor berbeda.
- **Kualitas aturan:** konsekuen dibuat dengan sistem poin berbobot. Bobot (IPK & penghasilan ×3) adalah pilihan kebijakan; panitia lain bisa memberi bobot berbeda.
- **Data simulasi:** 24 data dibuat untuk menguji perilaku sistem, bukan data mahasiswa sebenarnya, sehingga belum bisa diukur akurasinya terhadap keputusan panitia riil.
- **Sifat centroid:** skor tidak pernah mencapai 0 atau 100 (rentang 13,03–86,97), dan dapat sedikit tidak monoton (< 1 poin) di daerah tumpang tindih.
- **Grid diskrit 0,5:** menimbulkan selisih ≤ 0,14 poin dibanding integral kontinu.
- **Skor adalah rekomendasi**, bukan keputusan final.
