# Anggota 3 — Programmer Mamdani

**Nama:** [Nama]

## Apa yang saya kerjakan

1. Memprogram **5 tahap metode Mamdani**, dari input angka sampai skor akhir.
2. Menyiapkan **contoh perhitungan lengkap** untuk satu mahasiswa (M10).
3. Menentukan **label rekomendasi** dari skor.

Bagian kode: `fuzzifikasi()`, `alpha_aturan()`, `infer()`, dan `label_keputusan()` di `fuzzy_beasiswa.py`.
Cara mencoba: `python fuzzy_beasiswa.py --ipk 3.25 --peng 8 --tang 5 --pres 70`

---

## 1. Lima tahap Mamdani

| Tahap | Yang terjadi | Aturan tugas |
|---|---|---|
| 1. Fuzzifikasi | Angka diubah menjadi derajat (0–1) per kategori | — |
| 2. α-predikat | Kekuatan aturan = **nilai terkecil** dari 4 syaratnya | AND = MIN |
| 3. Implikasi | Grafik hasil aturan **dipotong** setinggi kekuatannya | MIN |
| 4. Agregasi | Semua potongan **digabung**, diambil bagian tertinggi | MAX |
| 5. Defuzzifikasi | Dicari **titik berat** gabungan, dan itulah skornya | Centroid |

Untuk mencari titik berat, program menghitung skor 0 sampai 100 setiap **0,5 langkah**.

**Gambaran mudahnya:** setiap aturan seperti juri yang memberi suara. Suara juri sekuat syarat terlemahnya (MIN). Semua suara digabung (MAX), lalu skor akhir adalah “titik tengah” dari gabungan suara itu (centroid).

## 2. Contoh lengkap: mahasiswa M10

**Data:** IPK 3,25 · Penghasilan Rp 8 juta · Tanggungan 5 · Prestasi 70

### Tahap 1 — Fuzzifikasi

| Input | Hasil |
|---|---|
| IPK 3,25 | setengah Sedang, setengah Tinggi |
| Penghasilan 8 jt | ⅔ Sedang, ⅓ Tinggi |
| Tanggungan 5 | setengah Sedang, setengah Banyak |
| Prestasi 70 | setengah Sedang, setengah Tinggi |

Setiap input masuk 2 kategori, jadi ada **2 × 2 × 2 × 2 = 16 aturan aktif**.

### Tahap 2 — Kekuatan aturan (MIN)

Contoh aturan R41 (semua syarat Sedang):

```
min(½, ⅔, ½, ½) = ½   → hasil: Cukup layak
```

Contoh aturan R32 (sama, tetapi penghasilan **Tinggi**):

```
min(½, ⅓, ½, ½) = ⅓   → hasil: Tidak layak
```

### Tahap 3 — Pemotongan (implikasi)

Dari 16 aturan, ambil yang terkuat untuk setiap hasil:

| Hasil | Dipotong setinggi |
|---|---|
| Tidak layak | ⅓ |
| Cukup layak | ½ |
| Layak | ½ |
| Sangat layak | ½ |

### Tahap 4 — Penggabungan (agregasi)

Keempat potongan ditumpuk. Hasilnya berbentuk “dataran”: rendah (⅓) di bagian kiri dan lebih tinggi (½) di tengah sampai kanan.

### Tahap 5 — Skor (centroid)

Titik berat dataran tersebut berada di sekitar **54**. Program menghasilkan **53,77**, dan hitungan tangan menghasilkan **53,74** (hampir sama).

Skor 54 masuk rentang **52,5 – 75**, jadi rekomendasinya **Layak** ✅

## 3. Label rekomendasi

| Skor | Rekomendasi |
|---|---|
| di bawah 27,5 | Tidak layak |
| 27,5 – 52,5 | Cukup layak |
| 52,5 – 75 | Layak |
| 75 ke atas | Sangat layak |

Angka batas ini adalah titik pertemuan grafik output. Kalau skor tepat di batas, dipilih kategori yang **lebih tinggi**.

## 4. Bagian pengujian saya

- **Validasi:** mencocokkan program dengan hitungan manual pada 5 mahasiswa. Selisihnya **di bawah 0,2 poin**.
- **Sensitivitas:** mengubah satu input sedikit demi sedikit dan melihat perubahan skornya.

Detailnya ada di [pengujian_bersama.md](pengujian_bersama.md).

---

## Persiapan tanya jawab

**T: Kenapa kekuatan aturan memakai MIN?**
J: Karena syaratnya memakai AND: semua syarat harus terpenuhi, jadi aturan hanya sekuat syarat yang paling lemah.

**T: Apa bedanya implikasi dan agregasi?**
J: Implikasi memotong hasil satu aturan. Agregasi menggabungkan hasil semua aturan.

**T: Kenapa skor tidak pernah 0 atau 100?**
J: Centroid adalah titik berat sebuah bidang, dan titik berat tidak bisa berada tepat di ujung. Skor terendah sekitar 13 dan tertinggi sekitar 87. Ini normal.

**T: Kenapa hasil program dan hitungan tangan beda sedikit?**
J: Program menghitung per langkah 0,5, sedangkan hitungan tangan memakai integral. Selisihnya sangat kecil.
