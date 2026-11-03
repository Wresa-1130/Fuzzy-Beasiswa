# -*- coding: utf-8 -*-
"""
SPK Kelayakan Penerima Beasiswa - Logika Fuzzy Metode Mamdani
Tugas Projek Logika Fuzzy

Operator   : AND = MIN, implikasi = MIN, agregasi = MAX, defuzzifikasi = centroid
Grid output: z = 0, 0.5, 1.0, ..., 100 (201 titik, interval 0,5)

Cara pakai
  python fuzzy_beasiswa.py                      -> jalankan seluruh pengujian, validasi,
                                                   sensitivitas, simpan grafik/CSV/JSON
  python fuzzy_beasiswa.py --ipk 3.4 --peng 4 --tang 5 --pres 70
                                                -> hitung satu mahasiswa

Kebutuhan: numpy, pandas, matplotlib  (sudah tersedia di Google Colab)
"""
import argparse
import json
import os

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT_DIR = "hasil_fuzzy"
INPUTS = ["IPK", "Penghasilan", "Tanggungan", "Prestasi"]
OUTPUT = "Kelayakan"

# ----------------------------------------------------------------------------
# 1. FUNGSI KEANGGOTAAN  (semua parameter ada di sini agar mudah diperiksa)
#    ("tri", (a,b,c))      -> segitiga
#    ("trap", (a,b,c,d))   -> trapesium (bahu kiri: a=b ; bahu kanan: c=d)
#    Input memakai partisi Ruspini: himpunan bertetangga selalu berjumlah 1,
#    berpotongan di mu = 0,5 -> tidak ada celah dan skor lebih monoton.
# ----------------------------------------------------------------------------
VAR = {
    "IPK": {
        "semesta": (0, 4), "satuan": "skala 0-4",
        "himpunan": {
            "Rendah": ("trap", (0, 0, 2.5, 3.0)),
            "Sedang": ("tri", (2.5, 3.0, 3.5)),
            "Tinggi": ("trap", (3.0, 3.5, 4.0, 4.0)),
        },
    },
    "Penghasilan": {
        "semesta": (0, 15), "satuan": "juta Rp/bulan",
        "himpunan": {
            "Rendah": ("trap", (0, 0, 2, 5)),
            "Sedang": ("trap", (2, 5, 7, 10)),
            "Tinggi": ("trap", (7, 10, 15, 15)),
        },
    },
    "Tanggungan": {
        "semesta": (0, 8), "satuan": "orang",
        "himpunan": {
            "Sedikit": ("trap", (0, 0, 1, 3)),
            "Sedang": ("trap", (1, 3, 4, 6)),
            "Banyak": ("trap", (4, 6, 8, 8)),
        },
    },
    "Prestasi": {
        "semesta": (0, 100), "satuan": "skor 0-100",
        "himpunan": {
            "Rendah": ("trap", (0, 0, 30, 50)),
            "Sedang": ("trap", (30, 50, 60, 80)),
            "Tinggi": ("trap", (60, 80, 100, 100)),
        },
    },
    "Kelayakan": {
        "semesta": (0, 100), "satuan": "skor 0-100",
        "himpunan": {
            "Tidak layak": ("trap", (0, 0, 15, 35)),
            "Cukup layak": ("tri", (20, 40, 60)),
            "Layak": ("tri", (45, 65, 85)),
            "Sangat layak": ("trap", (65, 85, 100, 100)),
        },
    },
}


def trapmf(x, a, b, c, d):
    """Fungsi keanggotaan trapesium (juga menangani bahu a=b atau c=d)."""
    x = float(x)
    if x < a or x > d:
        return 0.0
    if b <= x <= c:
        return 1.0
    if x < b:
        return (x - a) / (b - a)
    return (d - x) / (d - c)


def mu(var, himpunan, x):
    tipe, p = VAR[var]["himpunan"][himpunan]
    if tipe == "tri":
        a, b, c = p
        return trapmf(x, a, b, b, c)
    return trapmf(x, *p)


# ----------------------------------------------------------------------------
# 2. BASIS ATURAN - faktorial lengkap 3x3x3x3 = 81 aturan
#    Setiap kombinasi kategori diberi poin (0/1/2) lalu dibobot:
#    IPK x3, Penghasilan x3, Tanggungan x2, Prestasi x2  -> total 0..20
#    Total <= 7 : Tidak layak | 8-11 : Cukup layak | 12-15 : Layak | >= 16 : Sangat layak
#    Karena SEMUA kombinasi kategori punya aturan, tidak ada celah cakupan.
# ----------------------------------------------------------------------------
TL, CL, L, SL = "Tidak layak", "Cukup layak", "Layak", "Sangat layak"
_KATEGORI = {  # urutan: poin 0, 1, 2 (poin besar = lebih mendukung kelayakan)
    "IPK": ["Rendah", "Sedang", "Tinggi"],
    "Penghasilan": ["Tinggi", "Sedang", "Rendah"],
    "Tanggungan": ["Sedikit", "Sedang", "Banyak"],
    "Prestasi": ["Rendah", "Sedang", "Tinggi"],
}
_BOBOT = {"IPK": 3, "Penghasilan": 3, "Tanggungan": 2, "Prestasi": 2}


def _keluaran(total):
    if total <= 7:
        return TL
    if total <= 11:
        return CL
    if total <= 15:
        return L
    return SL


RULES = []
for _i in range(3):
    for _p in range(3):
        for _t in range(3):
            for _r in range(3):
                _tot = 3 * _i + 3 * _p + 2 * _t + 2 * _r
                RULES.append(dict(no=len(RULES) + 1,
                                  IPK=_KATEGORI["IPK"][_i], Penghasilan=_KATEGORI["Penghasilan"][_p],
                                  Tanggungan=_KATEGORI["Tanggungan"][_t], Prestasi=_KATEGORI["Prestasi"][_r],
                                  poin=_tot, out=_keluaran(_tot)))

# ----------------------------------------------------------------------------
# 3. MESIN INFERENSI MAMDANI
# ----------------------------------------------------------------------------
Z = np.arange(0, 100.0001, 0.5)  # grid output, interval 0,5
OUT_MU = {k: np.array([mu(OUTPUT, k, z) for z in Z]) for k in VAR[OUTPUT]["himpunan"]}


def fuzzifikasi(x):
    return {v: {h: mu(v, h, x[v]) for h in VAR[v]["himpunan"]} for v in INPUTS}


def alpha_aturan(fz):
    """alpha-predikat tiap aturan, AND = MIN."""
    hasil = []
    for r in RULES:
        nilai = [fz[v][r[v]] for v in INPUTS if r[v] is not None]
        hasil.append(min(nilai))
    return hasil


def label_keputusan(skor):
    """Himpunan output dengan derajat tertinggi pada skor crisp.
    Seri di titik silang (27,5 / 52,5 / 75) -> pilih kategori yang lebih tinggi."""
    derajat = {k: mu(OUTPUT, k, skor) for k in VAR[OUTPUT]["himpunan"]}
    tertinggi = max(derajat.values())
    return [k for k, d in derajat.items() if d >= tertinggi - 1e-9][-1]


def infer(ipk, peng, tang, pres):
    x = {"IPK": ipk, "Penghasilan": peng, "Tanggungan": tang, "Prestasi": pres}
    for v in INPUTS:  # validasi semesta
        lo, hi = VAR[v]["semesta"]
        if not lo <= x[v] <= hi:
            raise ValueError(f"{v}={x[v]} di luar semesta [{lo}, {hi}]")
    fz = fuzzifikasi(x)
    alpha = alpha_aturan(fz)
    agg = np.zeros_like(Z)
    for r, a in zip(RULES, alpha):
        agg = np.maximum(agg, np.minimum(a, OUT_MU[r["out"]]))  # implikasi MIN, agregasi MAX
    if agg.sum() == 0:
        raise RuntimeError("Tidak ada aturan aktif (celah basis aturan)")
    skor = float((Z * agg).sum() / agg.sum())  # centroid diskrit
    alpha_out = {k: 0.0 for k in VAR[OUTPUT]["himpunan"]}
    for r, a in zip(RULES, alpha):
        alpha_out[r["out"]] = max(alpha_out[r["out"]], a)
    return dict(x=x, fuzz=fz, alpha=alpha, alpha_out=alpha_out, agg=agg,
                skor=skor, label=label_keputusan(skor))


# ----------------------------------------------------------------------------
# 4. DATA SIMULASI (24 mahasiswa)
# ----------------------------------------------------------------------------
DATA = [
    # id, IPK, penghasilan (juta), tanggungan, prestasi, jenis uji, keterangan
    ("M01", 4.00, 0.0, 8, 100, "Ekstrem", "Semua kriteria paling mendukung"),
    ("M02", 0.00, 15.0, 0, 0, "Ekstrem", "Semua kriteria paling tidak mendukung"),
    ("M03", 4.00, 15.0, 0, 100, "Ekstrem", "Akademik maksimum, kebutuhan ekonomi minimum"),
    ("M04", 0.00, 0.0, 8, 0, "Ekstrem", "Akademik minimum, kebutuhan ekonomi maksimum"),
    ("M05", 3.00, 5.0, 3, 50, "Titik batas", "Puncak IPK sedang; awal inti Sedang pada Penghasilan, Tanggungan, Prestasi"),
    ("M06", 2.50, 2.0, 1, 30, "Titik batas", "Ujung bahu Rendah/Sedikit di keempat variabel"),
    ("M07", 3.50, 10.0, 6, 80, "Titik batas", "Awal bahu Tinggi/Banyak di keempat variabel"),
    ("M08", 2.75, 3.5, 2, 40, "Titik batas", "Titik silang mu = 0,5 (Rendah/Sedang) di keempat variabel"),
    ("M09", 2.75, 4.0, 5, 40, "Tumpang tindih", "Beririsan di keempat variabel"),
    ("M10", 3.25, 8.0, 5, 70, "Tumpang tindih", "Beririsan di keempat variabel (contoh perhitungan lengkap)"),
    ("M11", 3.10, 6.5, 3.5, 55, "Tumpang tindih", "Mendekati nilai tengah di semua variabel"),
    ("M12", 3.90, 14.0, 1, 90, "Kontradiktif", "Akademik tinggi, ekonomi mampu, tanggungan sedikit"),
    ("M13", 2.10, 1.0, 7, 85, "Kontradiktif", "IPK rendah, ekonomi lemah, tanggungan banyak, prestasi tinggi"),
    ("M14", 3.80, 1.5, 0, 10, "Kontradiktif", "IPK tinggi, ekonomi lemah, tanpa tanggungan, prestasi rendah"),
    ("M15", 2.00, 12.0, 2, 95, "Kontradiktif", "IPK rendah, ekonomi mampu, prestasi sangat tinggi"),
    ("M16", 3.70, 2.5, 5, 75, "Umum", "Profil kuat dan membutuhkan"),
    ("M17", 3.40, 4.5, 4, 60, "Umum", "Profil menengah ke atas"),
    ("M18", 3.00, 7.0, 3, 45, "Umum", "Profil menengah"),
    ("M19", 2.60, 9.0, 2, 35, "Umum", "Profil menengah ke bawah"),
    ("M20", 3.60, 11.0, 5, 65, "Umum", "IPK tinggi tetapi penghasilan tinggi"),
    ("M21", 2.90, 3.5, 6, 70, "Umum", "Kebutuhan tinggi, akademik sedang"),
    ("M22", 3.20, 5.5, 7, 20, "Umum", "Tanggungan banyak, prestasi rendah"),
    ("M23", 4.00, 7.0, 4, 60, "Titik batas", "IPK di batas atas semesta"),
    ("M24", 3.00, 15.0, 8, 100, "Titik batas", "Penghasilan dan tanggungan di batas atas semesta"),
]
KOLOM = ["ID", "IPK", "Penghasilan", "Tanggungan", "Prestasi", "Jenis uji", "Keterangan"]
CONTOH = "M10"  # mahasiswa untuk perhitungan lengkap


# ----------------------------------------------------------------------------
# 5. PERHITUNGAN MANUAL INDEPENDEN (untuk validasi)
#    Ditulis ulang tanpa memakai fungsi infer()/trapmf() di atas; integrasi
#    centroid memakai langkah 0,01 (jauh lebih halus daripada grid program, 0,5).
# ----------------------------------------------------------------------------
def hitung_manual(ipk, peng, tang, pres, langkah=0.01):
    def segitiga(x, a, b, c):
        if x <= a or x >= c:
            return 0.0
        return (x - a) / (b - a) if x <= b else (c - x) / (c - b)

    def trapesium(x, a, b, c, d):
        if x < a or x > d:
            return 0.0
        if x < b:
            return (x - a) / (b - a)
        if x <= c:
            return 1.0
        return (d - x) / (d - c)

    def derajat(var, h, x):
        t, p = VAR[var]["himpunan"][h]
        return segitiga(x, *p) if t == "tri" else trapesium(x, *p)

    nilai = {"IPK": ipk, "Penghasilan": peng, "Tanggungan": tang, "Prestasi": pres}
    alpha = []
    for r in RULES:
        m = [derajat(v, r[v], nilai[v]) for v in INPUTS if r[v] is not None]
        alpha.append(min(m))
    n = int(round(100 / langkah))
    pembilang = penyebut = 0.0
    for i in range(n + 1):
        z = i * langkah
        mz = 0.0
        for r, a in zip(RULES, alpha):
            mz = max(mz, min(a, derajat(OUTPUT, r["out"], z)))
        pembilang += z * mz
        penyebut += mz
    return pembilang / penyebut, alpha


# ----------------------------------------------------------------------------
# 6. PENGUJIAN, COVERAGE, SENSITIVITAS
# ----------------------------------------------------------------------------
def jalankan_pengujian():
    baris = []
    for d in DATA:
        h = infer(*d[1:5])
        baris.append(dict(zip(KOLOM, d), Skor=round(h["skor"], 2), Keputusan=h["label"],
                          Aturan_aktif=int(sum(a > 0 for a in h["alpha"])),
                          Alpha_maks=round(max(h["alpha"]), 3)))
    return pd.DataFrame(baris)


def cek_coverage():
    """Pindai grid 4 dimensi: adakah kombinasi input valid dengan semua aturan alpha = 0?"""
    sumbu = {
        "IPK": np.round(np.arange(0, 4.0001, 0.1), 4),
        "Penghasilan": np.round(np.arange(0, 15.0001, 0.5), 4),
        "Tanggungan": np.round(np.arange(0, 8.0001, 0.5), 4),
        "Prestasi": np.round(np.arange(0, 100.0001, 5), 4),
    }
    mu_ax = {v: {h: np.array([mu(v, h, x) for x in sumbu[v]]) for h in VAR[v]["himpunan"]}
             for v in INPUTS}
    bentuk = [len(sumbu[v]) for v in INPUTS]

    def bc(arr, idx):
        s = [1] * 4
        s[idx] = -1
        return arr.reshape(s)

    maks_semua = np.zeros(bentuk)
    maks_per_aturan = []
    for r in RULES:
        a = np.ones(bentuk)
        for i, v in enumerate(INPUTS):
            if r[v] is not None:
                a = np.minimum(a, bc(mu_ax[v][r[v]], i))
        maks_per_aturan.append(float(a.max()))
        maks_semua = np.maximum(maks_semua, a)
    return dict(jumlah_titik=int(maks_semua.size),
                titik_tanpa_aturan=int((maks_semua <= 0).sum()),
                alpha_maks_terkecil=float(maks_semua.min()),
                alpha_maks_per_aturan=maks_per_aturan)


def cek_semesta_himpunan():
    """Setiap titik semesta tiap variabel harus punya derajat > 0 pada minimal satu himpunan."""
    hasil = {}
    for v in VAR:
        lo, hi = VAR[v]["semesta"]
        xs = np.linspace(lo, hi, 4001)
        tertinggi = [max(mu(v, h, x) for h in VAR[v]["himpunan"]) for x in xs]
        hasil[v] = dict(min_derajat_maks=float(min(tertinggi)))
    return hasil


BASE = {"IPK": 3.2, "Penghasilan": 6.0, "Tanggungan": 4, "Prestasi": 60}


def sensitivitas():
    langkah = {"IPK": 0.25, "Penghasilan": 1.0, "Tanggungan": 1.0, "Prestasi": 10.0}
    hasil = {}
    for v in INPUTS:
        lo, hi = VAR[v]["semesta"]
        nilai = np.round(np.arange(lo, hi + 1e-9, langkah[v]), 4)
        skor = []
        for n in nilai:
            x = dict(BASE)
            x[v] = float(n)
            skor.append(round(infer(x["IPK"], x["Penghasilan"], x["Tanggungan"], x["Prestasi"])["skor"], 2))
        hasil[v] = dict(nilai=[float(n) for n in nilai], skor=skor)
    return hasil


# ----------------------------------------------------------------------------
# 7. GRAFIK
# ----------------------------------------------------------------------------
GAYA = [("tab:blue", "-"), ("tab:orange", "--"), ("tab:green", "-."), ("tab:red", ":")]


def plot_mf(var):
    lo, hi = VAR[var]["semesta"]
    xs = np.linspace(lo, hi, 1201)
    fig, ax = plt.subplots(figsize=(6.4, 2.9))
    for (h, _), (w, ls) in zip(VAR[var]["himpunan"].items(), GAYA):
        ax.plot(xs, [mu(var, h, x) for x in xs], color=w, ls=ls, lw=2, label=h)
    ax.set_xlim(lo, hi)
    ax.set_ylim(-0.03, 1.08)
    ax.set_xlabel(f"{var} ({VAR[var]['satuan']})")
    ax.set_ylabel("Derajat keanggotaan")
    ax.grid(alpha=0.3)
    ax.legend(loc="upper center", ncol=4, fontsize=8, bbox_to_anchor=(0.5, 1.2), frameon=False)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, f"mf_{var}.png"), dpi=200)
    plt.close(fig)


def plot_agregasi(h, nama):
    fig, ax = plt.subplots(figsize=(6.4, 3.2))
    for (k, _), (w, ls) in zip(VAR[OUTPUT]["himpunan"].items(), GAYA):
        ax.plot(Z, OUT_MU[k], color=w, ls=ls, lw=1, alpha=0.6, label=k)
    ax.fill_between(Z, h["agg"], color="gray", alpha=0.45, label="Hasil agregasi (MAX)")
    ax.axvline(h["skor"], color="black", lw=2, label=f"Centroid = {h['skor']:.2f}")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("Skor kelayakan")
    ax.set_ylabel("Derajat keanggotaan")
    ax.set_title(f"Agregasi dan centroid - {nama}", fontsize=10)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=7, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.2), frameon=False)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "agregasi_contoh.png"), dpi=200)
    plt.close(fig)


def plot_sensitivitas(sens):
    fig, axs = plt.subplots(2, 2, figsize=(6.6, 4.8))
    for ax, v in zip(axs.ravel(), INPUTS):
        ax.plot(sens[v]["nilai"], sens[v]["skor"], "o-", ms=3.5, lw=1.6)
        ax.set_xlabel(f"{v} ({VAR[v]['satuan']})", fontsize=8)
        ax.set_ylabel("Skor kelayakan", fontsize=8)
        ax.set_ylim(0, 100)
        ax.grid(alpha=0.3)
        ax.tick_params(labelsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "sensitivitas.png"), dpi=200)
    plt.close(fig)


def plot_hasil(df):
    fig, ax = plt.subplots(figsize=(6.6, 3.3))
    warna = {"Ekstrem": "tab:red", "Titik batas": "tab:purple", "Tumpang tindih": "tab:orange",
             "Kontradiktif": "tab:green", "Umum": "tab:blue"}
    ax.bar(df["ID"], df["Skor"], color=[warna[j] for j in df["Jenis uji"]])
    for y in (27.5, 52.5, 75):
        ax.axhline(y, color="gray", ls="--", lw=0.8)
    ax.set_ylim(0, 100)
    ax.set_ylabel("Skor kelayakan")
    ax.tick_params(axis="x", rotation=90, labelsize=7)
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in warna.values()]
    ax.legend(handles, warna.keys(), fontsize=7, ncol=5, loc="upper center",
              bbox_to_anchor=(0.5, 1.18), frameon=False)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "hasil_pengujian.png"), dpi=200)
    plt.close(fig)


# ----------------------------------------------------------------------------
# 8. PROGRAM UTAMA
# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ipk", type=float)
    ap.add_argument("--peng", type=float, help="penghasilan orang tua (juta Rp/bulan)")
    ap.add_argument("--tang", type=float, help="jumlah tanggungan")
    ap.add_argument("--pres", type=float, help="skor prestasi 0-100")
    a = ap.parse_args()

    if None not in (a.ipk, a.peng, a.tang, a.pres):
        h = infer(a.ipk, a.peng, a.tang, a.pres)
        print(f"Skor kelayakan = {h['skor']:.2f}  ->  {h['label']}")
        for v in INPUTS:
            print(f"  {v}: " + ", ".join(f"{k}={d:.3f}" for k, d in h["fuzz"][v].items()))
        for r, al in zip(RULES, h["alpha"]):
            if al > 0:
                print(f"  R{r['no']:<2d} alpha={al:.3f} -> {r['out']}")
        return

    os.makedirs(OUT_DIR, exist_ok=True)

    # grafik fungsi keanggotaan
    for v in VAR:
        plot_mf(v)

    # basis aturan + coverage
    cov = cek_coverage()
    sem = cek_semesta_himpunan()
    print("Coverage:", {k: v for k, v in cov.items() if k != "alpha_maks_per_aturan"})
    print("Semesta :", sem)

    # pengujian
    df = jalankan_pengujian()
    df.to_csv(os.path.join(OUT_DIR, "hasil_pengujian.csv"), index=False, encoding="utf-8-sig")
    plot_hasil(df)
    print(df[["ID", "IPK", "Penghasilan", "Tanggungan", "Prestasi", "Skor", "Keputusan",
              "Aturan_aktif"]].to_string(index=False))

    # contoh perhitungan lengkap
    c = next(d for d in DATA if d[0] == CONTOH)
    hc = infer(*c[1:5])
    plot_agregasi(hc, CONTOH)
    ringkas = []
    for z0 in range(0, 101, 5):
        i = int(z0 / 0.5)
        ringkas.append(dict(z=z0, mu=round(float(hc["agg"][i]), 4)))
    contoh = dict(
        id=CONTOH, x=hc["x"], fuzz=hc["fuzz"],
        aturan_aktif=[dict(no=r["no"], alpha=round(al, 4), out=r["out"],
                           kondisi={v: r[v] for v in INPUTS if r[v]})
                      for r, al in zip(RULES, hc["alpha"]) if al > 0],
        alpha_out={k: round(v, 4) for k, v in hc["alpha_out"].items()},
        tabel_z=ringkas,
        sum_mu=float(hc["agg"].sum()), sum_zmu=float((Z * hc["agg"]).sum()),
        skor=hc["skor"], label=hc["label"],
    )

    # validasi manual vs program
    kasus = ["M01", "M05", "M10", "M12", "M16"]
    validasi = []
    for k in kasus:
        d = next(t for t in DATA if t[0] == k)
        prog = infer(*d[1:5])["skor"]
        man, _ = hitung_manual(*d[1:5])
        validasi.append(dict(id=k, program=round(prog, 4), manual=round(man, 4),
                             selisih=round(abs(prog - man), 4)))
    print("Validasi:", validasi)

    # sensitivitas
    sens = sensitivitas()
    plot_sensitivitas(sens)
    for v in INPUTS:
        print(v, list(zip(sens[v]["nilai"], sens[v]["skor"])))
    pd.DataFrame({f"{v}_{k}": pd.Series(sens[v][k]) for v in INPUTS for k in ("nilai", "skor")}) \
        .to_csv(os.path.join(OUT_DIR, "sensitivitas.csv"), index=False)

    # simpan semuanya untuk laporan
    pd.DataFrame(RULES).to_csv(os.path.join(OUT_DIR, "aturan_fuzzy.csv"), index=False, encoding="utf-8-sig")
    with open(os.path.join(OUT_DIR, "results.json"), "w", encoding="utf-8") as f:
        json.dump(dict(var=VAR, rules=RULES, coverage=cov, semesta=sem,
                       tests=df.to_dict("records"), contoh=contoh, validasi=validasi,
                       sens=sens, base=BASE), f, ensure_ascii=False, indent=1)
    print(f"\nSelesai. Semua keluaran ada di folder '{OUT_DIR}/'")


if __name__ == "__main__":
    main()
