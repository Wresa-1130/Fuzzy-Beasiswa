# -*- coding: utf-8 -*-
"""
Web app Streamlit - SPK Kelayakan Beasiswa (Logika Fuzzy Mamdani)
Jalankan:  streamlit run app.py
Berkas fuzzy_beasiswa.py harus berada di folder yang sama.
"""
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

import fuzzy_beasiswa as fz

st.set_page_config(page_title="SPK Kelayakan Beasiswa (Fuzzy Mamdani)", page_icon="🎓", layout="wide")

GAYA = [("tab:blue", "-"), ("tab:orange", "--"), ("tab:green", "-."), ("tab:red", ":")]
LABEL = {"IPK": "IPK", "Penghasilan": "Penghasilan orang tua", "Tanggungan": "Jumlah tanggungan",
         "Prestasi": "Prestasi mahasiswa"}


def tampil(df, **kw):
    """st.dataframe lintas versi Streamlit (width='stretch' di versi baru)."""
    try:
        st.dataframe(df, hide_index=True, width="stretch", **kw)
    except TypeError:
        st.dataframe(df, hide_index=True, use_container_width=True, **kw)


def gambar(fig):
    """Tampilkan lalu tutup figure agar memori tidak bocor."""
    st.pyplot(fig)
    plt.close(fig)


def angka(v):
    return f"{v:g}"


def persamaan(tipe, p):
    """Persamaan LaTeX fungsi keanggotaan dari parameternya."""
    a, b, c, d = (p[0], p[1], p[1], p[2]) if tipe == "tri" else p
    baris = []
    if a < b:
        baris.append(rf"\frac{{x-{angka(a)}}}{{{angka(b - a)}}} & {angka(a)} \le x < {angka(b)}")
    baris.append(rf"1 & x = {angka(b)}" if b == c else rf"1 & {angka(b)} \le x \le {angka(c)}")
    if c < d:
        baris.append(rf"\frac{{{angka(d)}-x}}{{{angka(d - c)}}} & {angka(c)} < x \le {angka(d)}")
    baris.append(r"0 & \text{lainnya}")
    return r"\mu(x)=\begin{cases}" + r" \\ ".join(baris) + r"\end{cases}"


@st.cache_data
def data_pengujian():
    return fz.jalankan_pengujian(), fz.cek_coverage()


@st.cache_data
def data_validasi():
    baris = []
    for k in ["M01", "M05", "M10", "M12", "M16"]:
        d = next(t for t in fz.DATA if t[0] == k)
        prog = fz.infer(*d[1:5])["skor"]
        man, _ = fz.hitung_manual(*d[1:5])
        baris.append({"ID": k, "Program (grid 0,5)": round(prog, 4),
                      "Manual (langkah 0,01)": round(man, 4), "Selisih": round(abs(prog - man), 4)})
    return pd.DataFrame(baris), fz.sensitivitas()


def fig_mf(var, nilai=None):
    lo, hi = fz.VAR[var]["semesta"]
    xs = np.linspace(lo, hi, 801)
    fig, ax = plt.subplots(figsize=(5.2, 2.6))
    for (h, _), (w, ls) in zip(fz.VAR[var]["himpunan"].items(), GAYA):
        ax.plot(xs, [fz.mu(var, h, x) for x in xs], color=w, ls=ls, lw=2, label=h)
    if nilai is not None:
        ax.axvline(nilai, color="black", lw=1.5)
    ax.set_xlim(lo, hi)
    ax.set_ylim(-0.03, 1.08)
    ax.set_xlabel(f"{var} ({fz.VAR[var]['satuan']})")
    ax.set_ylabel("Derajat keanggotaan")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=7, ncol=4, loc="upper center", bbox_to_anchor=(0.5, 1.22), frameon=False)
    fig.tight_layout()
    return fig


def fig_agregasi(h):
    fig, ax = plt.subplots(figsize=(7, 3.2))
    for (k, _), (w, ls) in zip(fz.VAR[fz.OUTPUT]["himpunan"].items(), GAYA):
        ax.plot(fz.Z, fz.OUT_MU[k], color=w, ls=ls, lw=1, alpha=0.6, label=k)
    ax.fill_between(fz.Z, h["agg"], color="gray", alpha=0.45, label="Hasil agregasi (MAX)")
    ax.axvline(h["skor"], color="black", lw=2, label=f"Centroid = {h['skor']:.2f}")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("Skor kelayakan")
    ax.set_ylabel("Derajat keanggotaan")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=7, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.22), frameon=False)
    fig.tight_layout()
    return fig


# ------------------------------------------------------------------ sidebar
st.sidebar.header("Masukan data pendaftar")
st.sidebar.caption("Geser slider atau ketik nilai langsung pada kotak di bawahnya.")


def input_var(key, label, lo, hi, default, step, fmt):
    """Slider + number_input yang saling sinkron."""
    if key not in st.session_state:
        st.session_state[key] = default

    def dari_slider():
        st.session_state[key + "_n"] = st.session_state[key + "_s"]
        st.session_state[key] = st.session_state[key + "_s"]

    def dari_angka():
        st.session_state[key + "_s"] = st.session_state[key + "_n"]
        st.session_state[key] = st.session_state[key + "_n"]

    st.session_state.setdefault(key + "_s", default)
    st.session_state.setdefault(key + "_n", default)
    st.sidebar.slider(label, lo, hi, step=step, key=key + "_s", on_change=dari_slider, format=fmt)
    st.sidebar.number_input(f"{label} (ketik)", lo, hi, step=step, key=key + "_n",
                            on_change=dari_angka, format=fmt, label_visibility="collapsed")
    return st.session_state[key]


ipk = input_var("ipk", "IPK (0–4)", 0.0, 4.0, 3.25, 0.01, "%.2f")
peng = input_var("peng", "Penghasilan orang tua (juta Rp/bulan, 0–15)", 0.0, 15.0, 8.0, 0.1, "%.1f")
tang = input_var("tang", "Jumlah tanggungan (orang, 0–8)", 0, 8, 5, 1, "%d")
pres = input_var("pres", "Skor prestasi (0–100)", 0, 100, 70, 1, "%d")

# ------------------------------------------------------------------ hitung
hasil = fz.infer(ipk, peng, tang, pres)

st.title("🎓 SPK Kelayakan Penerima Beasiswa")
st.caption("Logika Fuzzy metode Mamdani · AND = MIN · implikasi = MIN · agregasi = MAX · "
           "defuzzifikasi centroid (grid 0,5)")

with st.expander("Tentang sistem"):
    st.markdown(
        "- **Tujuan:** membantu panitia menilai kelayakan pendaftar beasiswa secara konsisten.\n"
        "- **Pengguna:** panitia/admin seleksi beasiswa.\n"
        "- **Makna skor (0–100):** makin tinggi makin layak. Skor adalah *rekomendasi* "
        "pendukung keputusan, bukan keputusan akhir.\n"
        "- **Keterbatasan:** parameter dan aturan ditetapkan secara subjektif; pengujian memakai data simulasi.")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Hasil", "Fungsi keanggotaan", "Basis aturan",
                                        "Pengujian 24 data", "Validasi & sensitivitas"])

with tab1:
    c1, c2, c3 = st.columns(3)
    c1.metric("Skor kelayakan", f"{hasil['skor']:.2f}")
    c2.metric("Rekomendasi", hasil["label"])
    c3.metric("Aturan aktif", f"{sum(a > 0 for a in hasil['alpha'])} dari {len(fz.RULES)}")

    st.subheader("1. Fuzzifikasi")
    baris = []
    for v in fz.INPUTS:
        for h, d in hasil["fuzz"][v].items():
            baris.append({"Variabel": LABEL[v], "Himpunan": h, "Derajat keanggotaan (μ)": round(d, 4)})
    df_f = pd.DataFrame(baris)
    tampil(df_f)

    st.subheader("2. Aturan aktif dan α-predikat")
    aktif = []
    for r, a in zip(fz.RULES, hasil["alpha"]):
        if a > 0:
            mus = [hasil["fuzz"][v][r[v]] for v in fz.INPUTS]
            aktif.append({
                "Aturan": f"R{r['no']}",
                "IPK": r["IPK"], "Penghasilan": r["Penghasilan"],
                "Tanggungan": r["Tanggungan"], "Prestasi": r["Prestasi"],
                "α = min(μ)": round(a, 4),
                "Perhitungan": "min(" + "; ".join(f"{m:.3f}" for m in mus) + ")",
                "Keluaran": r["out"],
            })
    tampil(pd.DataFrame(aktif))

    st.subheader("3. Implikasi, agregasi, dan centroid")
    kiri, kanan = st.columns([3, 2])
    with kiri:
        gambar(fig_agregasi(hasil))
    with kanan:
        st.markdown("**α maksimum per himpunan keluaran (pemotong)**")
        tampil(pd.DataFrame({"Himpunan": list(hasil["alpha_out"]),
                             "α maks": [round(v, 4) for v in hasil["alpha_out"].values()]}))
        sm, szm = float(hasil["agg"].sum()), float((fz.Z * hasil["agg"]).sum())
        st.markdown(f"Σ μ(z) = **{sm:.3f}**  \nΣ z·μ(z) = **{szm:.3f}**  \n"
                    f"z* = Σ z·μ / Σ μ = **{szm / sm:.2f}**")
        st.caption("Label = himpunan keluaran dengan derajat tertinggi pada z* (seri → kategori lebih tinggi). "
                   "Batas: <27,5 Tidak layak; 27,5–<52,5 Cukup layak; 52,5–<75 Layak; ≥75 Sangat layak.")
    with st.expander("Tabel agregasi μ(z) tiap 5 poin"):
        idx = [int(z / 0.5) for z in range(0, 101, 5)]
        tampil(pd.DataFrame({"z": [float(fz.Z[i]) for i in idx],
                             "μ agregasi": [round(float(hasil["agg"][i]), 4) for i in idx]}))

with tab2:
    st.write("Garis hitam menunjukkan nilai masukan saat ini.")
    cols = st.columns(2)
    nilai = {"IPK": ipk, "Penghasilan": peng, "Tanggungan": tang, "Prestasi": pres}
    for i, v in enumerate(fz.INPUTS):
        with cols[i % 2]:
            st.markdown(f"**{LABEL[v]}**")
            gambar(fig_mf(v, nilai[v]))
    st.markdown("**Kelayakan beasiswa (keluaran)**")
    gambar(fig_mf("Kelayakan"))
    st.markdown("**Parameter**")
    prm = []
    for v in [*fz.INPUTS, fz.OUTPUT]:
        for h, (t, p) in fz.VAR[v]["himpunan"].items():
            prm.append({"Variabel": v, "Himpunan": h, "Bentuk": "Segitiga" if t == "tri" else "Trapesium",
                        "Parameter": str(tuple(p))})
    tampil(pd.DataFrame(prm))
    st.markdown("**Persamaan**")
    for v in [*fz.INPUTS, fz.OUTPUT]:
        with st.expander(v):
            for h, (t, p) in fz.VAR[v]["himpunan"].items():
                st.markdown(f"*{h}*")
                st.latex(persamaan(t, p))

with tab3:
    st.write(f"Basis aturan faktorial lengkap 3×3×3×3 = {len(fz.RULES)} aturan. Poin = 3·IPK + 3·Penghasilan "
             "+ 2·Tanggungan + 2·Prestasi (tiap kategori bernilai 0/1/2). "
             "Total ≤7 Tidak layak; 8–11 Cukup layak; 12–15 Layak; ≥16 Sangat layak.")
    df_r = pd.DataFrame(fz.RULES).rename(columns={"no": "No", "poin": "Poin", "out": "Kelayakan"})
    df_r["Aktif (α>0)"] = [round(a, 4) if a > 0 else None for a in hasil["alpha"]]
    tampil(df_r, height=500)

with tab4:
    df_u, cov = data_pengujian()
    st.write("Data simulasi: kondisi ekstrem, titik batas, tumpang tindih, kontradiktif, dan umum.")
    tampil(df_u)
    st.bar_chart(df_u.set_index("ID")["Skor"])
    st.markdown(f"**Cek cakupan aturan:** {cov['jumlah_titik']:,} kombinasi input diperiksa, "
                f"**{cov['titik_tanpa_aturan']}** tanpa aturan aktif, "
                f"α maksimum terkecil = **{cov['alpha_maks_terkecil']:.2f}**.")

with tab5:
    df_v, sens = data_validasi()
    st.subheader("Validasi program vs perhitungan manual")
    tampil(df_v)
    st.caption("Selisih kecil berasal dari beda resolusi grid centroid (0,5 vs 0,01).")
    st.subheader("Analisis sensitivitas")
    st.write("Satu input diubah bertahap, input lain tetap: "
             + ", ".join(f"{k} = {v}" for k, v in fz.BASE.items()) + ".")
    cols = st.columns(2)
    for i, v in enumerate(fz.INPUTS):
        with cols[i % 2]:
            st.markdown(f"**{LABEL[v]}**")
            st.line_chart(pd.DataFrame({"Skor": sens[v]["skor"]},
                                       index=pd.Index(sens[v]["nilai"], name=v)))
