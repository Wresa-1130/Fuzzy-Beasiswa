# Anggota 2 — Perancang Basis Aturan

**Nama:** [Nama]

## Apa yang saya kerjakan

1. Menyusun **aturan IF–THEN** yang menghubungkan 4 input ke hasil kelayakan.
2. Membuat **sistem poin** supaya aturan konsisten dan mudah diperiksa.
3. Memeriksa bahwa **setiap kemungkinan input pasti mengaktifkan aturan**.

Bagian kode: `RULES`, `_KATEGORI`, `_BOBOT`, dan `cek_coverage()` di `fuzzy_beasiswa.py`. Semua aturan bisa dilihat di tab **Basis aturan** pada web.

---

## 1. Bentuk aturan

```
IF IPK Tinggi AND Penghasilan Rendah AND Tanggungan Banyak AND Prestasi Tinggi
THEN Sangat layak
```

Setiap aturan memakai **keempat** input.

## 2. Kenapa 81 aturan?

Setiap input punya 3 kategori, jadi seluruh kombinasinya adalah:

**3 × 3 × 3 × 3 = 81 aturan**

Tugas meminta minimal 15 aturan. Kami membuat **semua kombinasi** supaya tidak ada kondisi mahasiswa yang terlewat.

## 3. Cara menentukan hasil tiap aturan: sistem poin

Daripada menebak satu per satu, setiap kategori diberi poin. **Makin mendukung kelayakan, makin besar poinnya.**

| Input | 0 poin | 1 poin | 2 poin | Dikali |
|---|---|---|---|---|
| IPK | Rendah | Sedang | Tinggi | ×3 |
| Penghasilan | Tinggi | Sedang | Rendah | ×3 |
| Tanggungan | Sedikit | Sedang | Banyak | ×2 |
| Prestasi | Rendah | Sedang | Tinggi | ×2 |

IPK dan penghasilan dikali 3 karena merupakan **kriteria utama** beasiswa: akademik dan kebutuhan ekonomi.

Total poin (0–20) lalu diubah menjadi hasil:

| Total poin | Hasil |
|---|---|
| 0 – 7 | Tidak layak |
| 8 – 11 | Cukup layak |
| 12 – 15 | Layak |
| 16 – 20 | Sangat layak |

### Contoh menghitung poin

Mahasiswa dengan IPK **Tinggi**, penghasilan **Rendah**, tanggungan **Banyak**, prestasi **Tinggi**:

```
IPK         Tinggi  = 2 × 3 = 6
Penghasilan Rendah  = 2 × 3 = 6
Tanggungan  Banyak  = 2 × 2 = 4
Prestasi    Tinggi  = 2 × 2 = 4
                     Total = 20 → Sangat layak
```

Mahasiswa dengan semua kategori **Sedang**: 3 + 3 + 2 + 2 = **10 → Cukup layak**.

## 4. Contoh aturan

| Aturan | IPK | Penghasilan | Tanggungan | Prestasi | Hasil |
|---|---|---|---|---|---|
| R1 | Rendah | Tinggi | Sedikit | Rendah | Tidak layak |
| R41 | Sedang | Sedang | Sedang | Sedang | Cukup layak |
| R55 | Tinggi | Tinggi | Sedikit | Rendah | Tidak layak |
| R27 | Rendah | Rendah | Banyak | Tinggi | Layak |
| R81 | Tinggi | Rendah | Banyak | Tinggi | Sangat layak |

## 5. Bukti tidak ada celah

Tugas mengingatkan bahwa banyaknya aturan **belum menjamin** semua kondisi tertangani. Karena itu kami mengujinya:

- Program mencoba **ratusan ribu kombinasi input**, dari nilai terkecil sampai terbesar.
- Hasilnya: **tidak ada satu pun** kombinasi yang tidak mengaktifkan aturan.
- Bahkan di kondisi terlemah, selalu ada aturan yang aktif dengan kekuatan minimal **½**.

Alasannya sederhana: setiap input pasti masuk minimal satu kategori, dan setiap kombinasi kategori punya aturan.

## 6. Bagian pengujian saya

- Uji **cakupan aturan** di atas.
- Menguji **data kontradiktif**, misalnya IPK tinggi tetapi orang tua kaya, dan memastikan hasilnya masuk akal.
- Menulis keterbatasan: **bobot aturan** adalah pilihan kelompok.

Detailnya ada di [pengujian_bersama.md](pengujian_bersama.md).

---

## Persiapan tanya jawab

**T: Kenapa tidak cukup 15 aturan saja?**
J: Dengan 15 aturan ada kombinasi yang tidak punya aturan, sehingga sistem bisa tidak menghasilkan jawaban. Dengan 81 aturan semuanya tertangani.

**T: Apakah ada aturan yang bertentangan?**
J: Tidak. Setiap kombinasi hanya punya satu aturan dengan satu hasil.

**T: Kenapa IPK dan penghasilan bobotnya lebih besar?**
J: Karena beasiswa umumnya menilai prestasi akademik dan kebutuhan ekonomi terlebih dahulu. Bobot ini pilihan kebijakan kelompok dan bisa diubah.

**T: Mahasiswa IPK tinggi tapi orang tuanya kaya, hasilnya apa?**
J: Cenderung *Cukup layak*, karena poin IPK yang tinggi diimbangi poin penghasilan yang rendah.
