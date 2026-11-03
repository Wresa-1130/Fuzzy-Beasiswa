# -*- coding: utf-8 -*-
"""
Uji otomatis SPK Fuzzy Mamdani.
Jalankan:  python test_fuzzy.py   (atau: pytest test_fuzzy.py)
"""
import itertools

import numpy as np

import fuzzy_beasiswa as fz

TOL = 1e-9


# ---------------------------------------------------------------- fungsi keanggotaan
def test_titik_kunci_mf():
    """Derajat di titik parameter sesuai rumus."""
    cek = [
        ("IPK", "Rendah", 2.5, 1.0), ("IPK", "Rendah", 2.75, 0.5), ("IPK", "Sedang", 3.0, 1.0),
        ("IPK", "Tinggi", 3.25, 0.5), ("IPK", "Tinggi", 4.0, 1.0),
        ("Penghasilan", "Rendah", 0, 1.0), ("Penghasilan", "Sedang", 6, 1.0),
        ("Penghasilan", "Tinggi", 8.5, 0.5), ("Penghasilan", "Tinggi", 15, 1.0),
        ("Tanggungan", "Sedikit", 2, 0.5), ("Tanggungan", "Sedang", 3.5, 1.0),
        ("Tanggungan", "Banyak", 8, 1.0),
        ("Prestasi", "Rendah", 40, 0.5), ("Prestasi", "Sedang", 55, 1.0), ("Prestasi", "Tinggi", 70, 0.5),
        ("Kelayakan", "Tidak layak", 27.5, 0.375), ("Kelayakan", "Cukup layak", 40, 1.0),
        ("Kelayakan", "Layak", 65, 1.0), ("Kelayakan", "Sangat layak", 100, 1.0),
    ]
    for v, h, x, harap in cek:
        assert abs(fz.mu(v, h, x) - harap) < TOL, (v, h, x, fz.mu(v, h, x))


def test_partisi_ruspini_dan_tanpa_celah():
    """Input: jumlah derajat = 1 di semua titik. Output: selalu ada derajat > 0."""
    for v in fz.VAR:
        lo, hi = fz.VAR[v]["semesta"]
        for x in np.linspace(lo, hi, 2001):
            d = [fz.mu(v, h, x) for h in fz.VAR[v]["himpunan"]]
            assert all(0 <= m <= 1 for m in d)
            if v in fz.INPUTS:
                assert abs(sum(d) - 1) < 1e-9, (v, x, d)
            else:
                assert max(d) > 0, (v, x)


# ---------------------------------------------------------------- basis aturan
def test_basis_aturan():
    assert len(fz.RULES) >= 15
    for v in fz.INPUTS:  # keempat variabel dipakai
        assert all(r[v] for r in fz.RULES)
    kombinasi = {tuple(r[v] for v in fz.INPUTS) for r in fz.RULES}
    assert len(kombinasi) == 81  # lengkap dan tidak ada duplikat/kontradiksi


def test_coverage_semua_input_mengaktifkan_aturan():
    cov = fz.cek_coverage()
    assert cov["titik_tanpa_aturan"] == 0
    assert cov["alpha_maks_terkecil"] >= 0.5 - TOL


# ---------------------------------------------------------------- mesin Mamdani
def test_operator_mamdani_dihitung_ulang():
    """Hitung ulang AND=MIN, implikasi=MIN, agregasi=MAX, centroid secara terpisah."""
    for d in fz.DATA:
        h = fz.infer(*d[1:5])
        agg = np.zeros_like(fz.Z)
        for r in fz.RULES:
            a = min(h["fuzz"][v][r[v]] for v in fz.INPUTS)
            agg = np.maximum(agg, np.minimum(a, fz.OUT_MU[r["out"]]))
        assert np.allclose(agg, h["agg"])
        assert abs(h["skor"] - (fz.Z * agg).sum() / agg.sum()) < 1e-9


def test_validasi_manual_minimal_tiga_kasus():
    for k in ["M01", "M05", "M10", "M16"]:
        d = next(t for t in fz.DATA if t[0] == k)
        prog = fz.infer(*d[1:5])["skor"]
        man, _ = fz.hitung_manual(*d[1:5], langkah=0.05)
        assert abs(prog - man) < 0.5, (k, prog, man)


def test_contoh_m10_sesuai_hitungan_tangan():
    """Nilai yang dihitung manual di PENJELASAN_SISTEM.md."""
    h = fz.infer(3.25, 8.0, 5, 70)
    f = h["fuzz"]
    assert abs(f["IPK"]["Sedang"] - 0.5) < TOL and abs(f["IPK"]["Tinggi"] - 0.5) < TOL
    assert abs(f["Penghasilan"]["Sedang"] - 2 / 3) < TOL and abs(f["Penghasilan"]["Tinggi"] - 1 / 3) < TOL
    assert abs(f["Tanggungan"]["Sedang"] - 0.5) < TOL and abs(f["Tanggungan"]["Banyak"] - 0.5) < TOL
    assert abs(f["Prestasi"]["Sedang"] - 0.5) < TOL and abs(f["Prestasi"]["Tinggi"] - 0.5) < TOL
    ao = h["alpha_out"]
    assert abs(ao["Tidak layak"] - 1 / 3) < TOL
    assert all(abs(ao[k] - 0.5) < TOL for k in ["Cukup layak", "Layak", "Sangat layak"])
    assert sum(a > 0 for a in h["alpha"]) == 16
    assert abs(h["skor"] - 53.7723) < 1e-3 and h["label"] == "Layak"


# ---------------------------------------------------------------- input & keputusan
def test_input_di_luar_semesta_ditolak():
    for args in [(-0.1, 5, 3, 50), (4.1, 5, 3, 50), (3, 16, 3, 50), (3, 5, 9, 50),
                 (3, 5, 3, 101), (float("nan"), 5, 3, 50)]:
        try:
            fz.infer(*args)
        except ValueError:
            continue
        raise AssertionError(f"tidak ditolak: {args}")


def test_label_di_titik_silang():
    assert fz.label_keputusan(27.4) == "Tidak layak"
    assert fz.label_keputusan(27.5) == "Cukup layak"
    assert fz.label_keputusan(52.5) == "Layak"
    assert fz.label_keputusan(75.0) == "Sangat layak"


def test_kasus_ekstrem():
    best = fz.infer(4, 0, 8, 100)
    worst = fz.infer(0, 15, 0, 0)
    assert best["label"] == "Sangat layak" and worst["label"] == "Tidak layak"
    assert best["skor"] > 80 and worst["skor"] < 20


def test_minimal_20_data_dan_jenis_uji():
    assert len(fz.DATA) >= 20
    jenis = {d[5] for d in fz.DATA}
    assert {"Ekstrem", "Titik batas", "Tumpang tindih", "Kontradiktif"} <= jenis
    df = fz.jalankan_pengujian()
    assert len(df) == len(fz.DATA) and df["Skor"].between(0, 100).all()


def test_arah_pengaruh_input():
    """Skor naik bila IPK/Tanggungan/Prestasi naik, turun bila Penghasilan naik.
    Mamdani MIN-MAX + centroid bisa sedikit tidak monoton; toleransi 1 poin."""
    arah = {"IPK": 1, "Penghasilan": -1, "Tanggungan": 1, "Prestasi": 1}
    kasar = {"IPK": [0, 2.75, 3, 3.25, 4], "Penghasilan": [0, 3.5, 6, 8.5, 15],
             "Tanggungan": [0, 2, 3.5, 5, 8], "Prestasi": [0, 40, 55, 70, 100]}
    halus = {v: np.linspace(*fz.VAR[v]["semesta"], 41) for v in fz.INPUTS}
    for v in fz.INPUTS:
        lain = [u for u in fz.INPUTS if u != v]
        for combo in itertools.product(*[kasar[u] for u in lain]):
            x = dict(zip(lain, combo))
            skor = []
            for t in halus[v]:
                x[v] = t
                skor.append(fz.infer(x["IPK"], x["Penghasilan"], x["Tanggungan"], x["Prestasi"])["skor"])
            beda = arah[v] * np.diff(skor)
            assert beda.min() > -1.0, (v, x, beda.min())
            assert arah[v] * (skor[-1] - skor[0]) >= -TOL  # ujung ke ujung searah


if __name__ == "__main__":
    tes = [(n, f) for n, f in globals().items() if n.startswith("test_")]
    for n, f in tes:
        f()
        print(f"LULUS  {n}")
    print(f"\nSemua {len(tes)} uji lulus.")
