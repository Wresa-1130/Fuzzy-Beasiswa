# Pembagian Tugas Kelompok

Ganti `[Nama]` dengan nama anggota.

| Anggota | Peran | Isi pekerjaan | File |
|---|---|---|---|
| 1 — [Nama] | Analis Masalah & Fungsi Keanggotaan | Tujuan sistem, variabel, grafik keanggotaan | [anggota1_fungsi_keanggotaan.md](anggota1_fungsi_keanggotaan.md) |
| 2 — [Nama] | Perancang Basis Aturan | 81 aturan IF–THEN, bukti tidak ada celah | [anggota2_basis_aturan.md](anggota2_basis_aturan.md) |
| 3 — [Nama] | Programmer Mamdani | Mesin hitung Mamdani, contoh perhitungan lengkap | [anggota3_mamdani.md](anggota3_mamdani.md) |
| 4 — [Nama] | Programmer Web | Tampilan web Streamlit | [anggota4_web.md](anggota4_web.md) |
| **Semua** | Pengujian | Setiap anggota menguji bagiannya sendiri | [pengujian_bersama.md](pengujian_bersama.md) |

## Alur kerja

```
Anggota 1        Anggota 2        Anggota 3         Anggota 4
Fungsi     →     Aturan     →     Mesin hitung →    Web
keanggotaan      IF–THEN          Mamdani           (tampilan)
     \_______________\________________\_________________/
                    Pengujian (dikerjakan bersama)
```

## Ringkasan sistem dalam 3 kalimat

1. Sistem menerima 4 data mahasiswa: **IPK, penghasilan orang tua, jumlah tanggungan, prestasi**.
2. Data tersebut diubah menjadi derajat “rendah/sedang/tinggi”, dicocokkan dengan aturan, lalu digabung memakai metode **Mamdani**.
3. Hasilnya berupa **skor 0–100** dan rekomendasi: Tidak layak, Cukup layak, Layak, atau Sangat layak.
