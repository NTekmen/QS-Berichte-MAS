import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# ── Seitenkonfiguration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="QS-Berichte Dashboard",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Hilfsfunktionen ────────────────────────────────────────────────────────────
SCHWEREGRAD_FARBEN = {
    "Kritisch": "#d62728",
    "Mittel": "#ff7f0e",
    "Gering": "#2ca02c",
}

STATUS_FARBEN = {
    "Offen": "#d62728",
    "In Bearbeitung": "#ff7f0e",
    "Behoben": "#2ca02c",
}


@st.cache_data
def lade_daten(pfad: str) -> pd.DataFrame:
    df = pd.read_csv(pfad, parse_dates=["Datum"])
    df["Monat"] = df["Datum"].dt.to_period("M").astype(str)
    df["KW"] = df["Datum"].dt.isocalendar().week.astype(int)
    df["Jahr"] = df["Datum"].dt.year
    return df


def metrik_karte(spalte, titel, wert, delta=None, delta_farbe="normal"):
    with spalte:
        st.metric(label=titel, value=wert, delta=delta, delta_color=delta_farbe)


# ── Daten laden ────────────────────────────────────────────────────────────────
DEFAULT_PFAD = Path(__file__).parent / "data" / "qs_berichte.csv"

st.sidebar.title("🔍 QS-Berichte MAS")
st.sidebar.markdown("---")

uploaded = st.sidebar.file_uploader(
    "📂 Eigene CSV-Datei hochladen",
    type=["csv"],
    help="Spalten: Datum, Abteilung, Produkt, Fehlerkategorie, Schweregrad, Status, Anzahl_Fehler, Prüfer, Bemerkung",
)

if uploaded:
    df_roh = pd.read_csv(uploaded, parse_dates=["Datum"])
    df_roh["Monat"] = df_roh["Datum"].dt.to_period("M").astype(str)
    df_roh["KW"] = df_roh["Datum"].dt.isocalendar().week.astype(int)
    df_roh["Jahr"] = df_roh["Datum"].dt.year
else:
    df_roh = lade_daten(str(DEFAULT_PFAD))

# ── Seitenleiste – Filter ──────────────────────────────────────────────────────
st.sidebar.markdown("### Filter")

abteilungen = ["Alle"] + sorted(df_roh["Abteilung"].unique().tolist())
abt_auswahl = st.sidebar.multiselect("Abteilung", abteilungen[1:], default=abteilungen[1:])

produkte = sorted(df_roh["Produkt"].unique().tolist())
prod_auswahl = st.sidebar.multiselect("Produkt", produkte, default=produkte)

schweregrade = sorted(df_roh["Schweregrad"].unique().tolist())
schw_auswahl = st.sidebar.multiselect("Schweregrad", schweregrade, default=schweregrade)

status_liste = sorted(df_roh["Status"].unique().tolist())
status_auswahl = st.sidebar.multiselect("Status", status_liste, default=status_liste)

min_datum = df_roh["Datum"].min().date()
max_datum = df_roh["Datum"].max().date()
datum_bereich = st.sidebar.date_input(
    "Zeitraum",
    value=(min_datum, max_datum),
    min_value=min_datum,
    max_value=max_datum,
)

# Datumsfilter sicher auswerten
if isinstance(datum_bereich, (list, tuple)) and len(datum_bereich) == 2:
    von_datum, bis_datum = datum_bereich
else:
    von_datum, bis_datum = min_datum, max_datum

# ── Daten filtern ──────────────────────────────────────────────────────────────
df = df_roh[
    (df_roh["Abteilung"].isin(abt_auswahl))
    & (df_roh["Produkt"].isin(prod_auswahl))
    & (df_roh["Schweregrad"].isin(schw_auswahl))
    & (df_roh["Status"].isin(status_auswahl))
    & (df_roh["Datum"].dt.date >= von_datum)
    & (df_roh["Datum"].dt.date <= bis_datum)
].copy()

# ── Seitentitel ────────────────────────────────────────────────────────────────
st.title("📊 QS-Berichte Dashboard")
st.caption(f"Zeitraum: {von_datum.strftime('%d.%m.%Y')} – {bis_datum.strftime('%d.%m.%Y')}  |  {len(df)} Einträge")
st.markdown("---")

if df.empty:
    st.warning("⚠️ Keine Daten für die gewählten Filter vorhanden.")
    st.stop()

# ── KPI-Karten ─────────────────────────────────────────────────────────────────
gesamt_fehler = int(df["Anzahl_Fehler"].sum())
gesamt_berichte = len(df)
kritische_fehler = int(df[df["Schweregrad"] == "Kritisch"]["Anzahl_Fehler"].sum())
offene_berichte = len(df[df["Status"] == "Offen"])
behobene_berichte = len(df[df["Status"] == "Behoben"])
behebungsquote = round(behobene_berichte / gesamt_berichte * 100, 1) if gesamt_berichte else 0

k1, k2, k3, k4, k5 = st.columns(5)
metrik_karte(k1, "📋 Berichte gesamt", gesamt_berichte)
metrik_karte(k2, "🔢 Fehler gesamt", gesamt_fehler)
metrik_karte(k3, "🚨 Kritische Fehler", kritische_fehler, delta_farbe="inverse")
metrik_karte(k4, "🔴 Offen", offene_berichte, delta_farbe="inverse")
metrik_karte(k5, "✅ Behebungsquote", f"{behebungsquote} %")

st.markdown("---")

# ── Zeile 1: Trend + Fehlerkategorien ─────────────────────────────────────────
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📈 Fehlerentwicklung (monatlich)")
    trend = (
        df.groupby("Monat")["Anzahl_Fehler"]
        .sum()
        .reset_index()
        .sort_values("Monat")
    )
    fig_trend = px.bar(
        trend,
        x="Monat",
        y="Anzahl_Fehler",
        labels={"Monat": "Monat", "Anzahl_Fehler": "Anzahl Fehler"},
        color_discrete_sequence=["#1f77b4"],
        text_auto=True,
    )
    fig_trend.update_layout(margin=dict(t=20, b=20), height=320)
    st.plotly_chart(fig_trend, use_container_width=True)

with col2:
    st.subheader("🗂️ Fehlerkategorien")
    kat = df.groupby("Fehlerkategorie")["Anzahl_Fehler"].sum().reset_index()
    fig_pie = px.pie(
        kat,
        names="Fehlerkategorie",
        values="Anzahl_Fehler",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig_pie.update_layout(margin=dict(t=20, b=20), height=320, showlegend=True)
    st.plotly_chart(fig_pie, use_container_width=True)

# ── Zeile 2: Abteilungen + Status ─────────────────────────────────────────────
col3, col4 = st.columns([1, 1])

with col3:
    st.subheader("🏭 Fehler je Abteilung")
    abt = (
        df.groupby(["Abteilung", "Schweregrad"])["Anzahl_Fehler"]
        .sum()
        .reset_index()
    )
    fig_abt = px.bar(
        abt,
        x="Abteilung",
        y="Anzahl_Fehler",
        color="Schweregrad",
        color_discrete_map=SCHWEREGRAD_FARBEN,
        labels={"Anzahl_Fehler": "Anzahl Fehler"},
        barmode="stack",
        text_auto=True,
    )
    fig_abt.update_layout(margin=dict(t=20, b=20), height=320)
    st.plotly_chart(fig_abt, use_container_width=True)

with col4:
    st.subheader("📌 Status-Übersicht")
    stat = df.groupby("Status")["Anzahl_Fehler"].sum().reset_index()
    fig_stat = px.bar(
        stat,
        x="Status",
        y="Anzahl_Fehler",
        color="Status",
        color_discrete_map=STATUS_FARBEN,
        labels={"Anzahl_Fehler": "Anzahl Fehler"},
        text_auto=True,
    )
    fig_stat.update_layout(margin=dict(t=20, b=20), height=320, showlegend=False)
    st.plotly_chart(fig_stat, use_container_width=True)

# ── Zeile 3: Produkt-Heatmap ───────────────────────────────────────────────────
st.subheader("🔥 Heatmap: Fehler nach Produkt & Fehlerkategorie")
heat_data = df.pivot_table(
    index="Produkt",
    columns="Fehlerkategorie",
    values="Anzahl_Fehler",
    aggfunc="sum",
    fill_value=0,
)
fig_heat = px.imshow(
    heat_data,
    text_auto=True,
    color_continuous_scale="Reds",
    labels={"color": "Fehler"},
    aspect="auto",
)
fig_heat.update_layout(margin=dict(t=20, b=20), height=280)
st.plotly_chart(fig_heat, use_container_width=True)

st.markdown("---")

# ── Datentabelle ───────────────────────────────────────────────────────────────
with st.expander("📄 Rohdaten anzeigen", expanded=False):
    anzeigespalten = ["Datum", "Abteilung", "Produkt", "Fehlerkategorie", "Schweregrad", "Status", "Anzahl_Fehler", "Prüfer", "Bemerkung"]
    vorhandene_spalten = [s for s in anzeigespalten if s in df.columns]
    st.dataframe(
        df[vorhandene_spalten].sort_values("Datum", ascending=False).reset_index(drop=True),
        use_container_width=True,
        height=400,
    )

    csv_export = df[vorhandene_spalten].to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Als CSV herunterladen",
        data=csv_export,
        file_name="qs_berichte_export.csv",
        mime="text/csv",
    )

st.sidebar.markdown("---")
from datetime import datetime as _dt
st.sidebar.caption(f"QS-Berichte MAS © {_dt.now().year}")


