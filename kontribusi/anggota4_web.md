# Anggota 4 — Programmer Web

**Nama:** [Nama]

## Apa yang saya kerjakan

1. Membuat **web** dengan Streamlit supaya sistem bisa dipakai tanpa mengetik kode.
2. Menampilkan **semua tahap hitungan** sehingga bisa diperiksa, sesuai syarat tugas.
3. Membuat **form input** yang mudah dan aman.

Bagian kode: seluruh `app.py`. Web ini memanggil mesin hitung dari `fuzzy_beasiswa.py` (buatan Anggota 3).
Cara menjalankan: `streamlit run app.py`, lalu buka `http://localhost:8501`.

---

## 1. Tampilan web

**Sisi kiri (sidebar):** tempat mengisi 4 data mahasiswa.

- Bisa memakai **slider** (digeser) atau **diketik** langsung.
- Slider dan kotak ketik **selalu sinkron**: mengubah salah satu ikut mengubah yang lain.
- Nilai dibatasi sesuai rentang, misalnya IPK hanya 0–4, sehingga input salah tidak bisa masuk.

**Bagian atas:** tombol **“Tentang sistem”** berisi tujuan, pengguna, makna skor, dan keterbatasan.

**5 tab utama:**

| Tab | Isi | Gunanya |
|---|---|---|
| Hasil | Skor, rekomendasi, jumlah aturan aktif, dan tabel tiap tahap | Melihat proses hitung untuk input saat ini |
| Fungsi keanggotaan | Grafik dan rumus tiap kategori | Garis hitam menunjukkan posisi input pada grafik |
| Basis aturan | Ke-81 aturan | Aturan yang sedang aktif ditandai nilainya |
| Pengujian 24 data | Tabel dan grafik batang hasil 24 mahasiswa | Bukti sistem sudah diuji |
| Validasi & sensitivitas | Perbandingan dengan hitungan manual dan grafik perubahan skor | Bukti hitungan benar |

## 2. Isi tab “Hasil” (urut sesuai tahap Mamdani)

1. **Tiga kotak angka di atas:** skor, rekomendasi, dan jumlah aturan aktif.
2. **Fuzzifikasi:** tabel derajat setiap kategori.
3. **Aturan aktif:** daftar aturan beserta cara hitung MIN-nya, misalnya `min(0.5; 0.667; 0.5; 0.5)`.
4. **Grafik agregasi:** daerah abu-abu adalah gabungan potongan, garis hitam adalah titik centroid (skor).
5. **Rumus centroid:** jumlah z·μ dibagi jumlah μ, ditulis lengkap.

Jadi siapa pun bisa **menelusuri angka dari input sampai skor** tanpa membuka kode.

## 3. Hal teknis yang saya perhatikan

- **Rumus otomatis:** rumus di tab Fungsi keanggotaan dibuat langsung dari parameter. Kalau parameter diubah, rumusnya ikut berubah sehingga tidak bisa salah tulis.
- **Cache:** pengujian 24 data dan sensitivitas hanya dihitung sekali, supaya web tidak lambat.
- **Grafik ditutup setelah tampil**, supaya memori komputer tidak penuh.

## 4. Bagian pengujian saya

Saya menguji web dengan beberapa cara:

| Uji | Hasil |
|---|---|
| Halaman dibuka | Tidak ada error, kelima tab tampil |
| Mengetik nilai terbaik (IPK 4, penghasilan 0, tanggungan 8, prestasi 100) | Sangat layak ✅ |
| Menggeser slider ke nilai terburuk | Tidak layak ✅ |
| Slider dan kotak ketik | Tetap sinkron ✅ |
| Mencoba nilai di luar batas | Tidak bisa dimasukkan ✅ |

Detail pengujian lainnya ada di [pengujian_bersama.md](pengujian_bersama.md).

---

## Persiapan tanya jawab

**T: Kenapa memakai Streamlit?**
J: Streamlit memakai Python, sama seperti mesin hitungnya, jadi web dan perhitungan cukup ditulis dalam satu bahasa. Membuat tabel dan grafik juga mudah.

**T: Apakah web menghitung sendiri atau memakai mesin dari Anggota 3?**
J: Memakai mesin dari Anggota 3 (`fuzzy_beasiswa.py`). Web hanya menampilkan hasilnya, jadi angkanya pasti sama dengan program utama.

**T: Bagaimana kalau pengguna salah input, misalnya IPK 5?**
J: Tidak bisa, karena slider dan kotak ketik sudah dibatasi 0–4. Mesin hitung juga menolak nilai di luar batas.

**T: Bagaimana cara membuktikan tahap hitungan bisa diperiksa?**
J: Buka tab Hasil: setiap tahap Mamdani ditampilkan dalam tabel dan grafik, lengkap dengan cara hitungnya.
