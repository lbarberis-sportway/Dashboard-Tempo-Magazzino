import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data_loader import load_and_process_data

# Funzione per formattazione italiana (es. 100.000,50)
def format_it(val, decimals=0):
    if pd.isna(val):
        return ""
    if decimals > 0:
        s = f"{val:,.{decimals}f}"
        return s.replace(",", "X").replace(".", ",").replace("X", ".")
    else:
        s = f"{val:,.0f}"
        return s.replace(",", ".")

# Configurazione della pagina
st.set_page_config(page_title="Dashboard Tempo di Stock", page_icon="logo.png", layout="wide")

# CSS Personalizzato per un look Premium
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
        color: #fafafa;
    }
    .metric-card {
        background-color: #1f2937;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        border-top: 4px solid #3b82f6;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #60a5fa;
    }
    .metric-label {
        font-size: 1rem;
        color: #9ca3af;
    }
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

st.title("Analisi Tempo di Stock Magazzino")

# Caricamento Dati
ENTRATE_PATH = "ENTRATE MAGAZZINO.xlsx"
USCITE_PATH = "USCITE MAGAZZINO.xlsx"

try:
    with st.spinner("Caricamento ed elaborazione dati in corso (FIFO)..."):
        df_entrate, df_uscite, df_matched = load_and_process_data(ENTRATE_PATH, USCITE_PATH)
except Exception as e:
    st.error(f"Errore durante il caricamento dei dati: {e}")
    st.stop()

if df_matched.empty:
    st.warning("Nessuna corrispondenza trovata tra Entrate e Uscite con i dati attuali.")
    st.stop()

# SIDEBAR - Filtri
st.sidebar.header("Filtri di Analisi")

# Filtro Data
min_date = df_matched['Data_Uscita'].min().date()
max_date = df_matched['Data_Uscita'].max().date()
date_range = st.sidebar.date_input("Periodo di Uscita", [min_date, max_date], min_value=min_date, max_value=max_date)

# Filtri Multipli
def get_unique(df, col):
    return sorted([str(x) for x in df[col].unique() if pd.notna(x)])

sel_categoria = st.sidebar.multiselect("Categoria", get_unique(df_matched, 'Categoria'), default=[])
sel_linea = st.sidebar.multiselect("Linea", get_unique(df_matched, 'Linea'), default=[])
sel_stagione = st.sidebar.multiselect("Stagione", get_unique(df_matched, 'Stagione'), default=[])
sel_produttore = st.sidebar.multiselect("Produttore", get_unique(df_matched, 'Produttore'), default=[])

# Applicazione Filtri
df_filtered = df_matched.copy()

if len(date_range) == 2:
    start_date, end_date = date_range
    df_filtered = df_filtered[(df_filtered['Data_Uscita'].dt.date >= start_date) & (df_filtered['Data_Uscita'].dt.date <= end_date)]

if sel_categoria:
    df_filtered = df_filtered[df_filtered['Categoria'].isin(sel_categoria)]
if sel_linea:
    df_filtered = df_filtered[df_filtered['Linea'].isin(sel_linea)]
if sel_stagione:
    df_filtered = df_filtered[df_filtered['Stagione'].isin(sel_stagione)]
if sel_produttore:
    df_filtered = df_filtered[df_filtered['Produttore'].isin(sel_produttore)]

st.markdown("---")

# SEZIONE KPI
col1, col2, col3, col4 = st.columns(4)

tempo_medio = df_filtered['Tempo_di_Stock_Giorni'].mean()
tot_qta_uscita = df_filtered['Quantita'].sum()
tot_qta_entrata = df_entrate['Quantita'].sum()
articoli_unici = df_filtered['Barcode'].nunique()

with col1:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{format_it(tempo_medio, 1)} gg</div><div class="metric-label">Tempo Medio di Giacenza</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{format_it(tot_qta_uscita)}</div><div class="metric-label">Quantità Totale Uscita</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{format_it(articoli_unici)}</div><div class="metric-label">Articoli Differenti</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{format_it(tot_qta_entrata)}</div><div class="metric-label">Totale Storico Entrate</div></div>', unsafe_allow_html=True)

st.write("")
st.write("")

# GRAFICI ANALITICI
colA, colB = st.columns(2)

with colA:
    st.subheader("Tempo Medio per Categoria")
    st.info("Top 20 categorie con la giacenza media più lunga.")
    # Streamlit disegna dal basso verso l'alto per grafici orizzontali,
    # quindi ordiniamo in ascending=True dopo aver preso i 20 più grandi
    df_cat = df_filtered.groupby('Categoria')['Tempo_di_Stock_Giorni'].mean().nlargest(20).sort_values(ascending=True)
    st.bar_chart(df_cat, horizontal=True)

with colB:
    st.subheader("Distribuzione Tempo di Stock (Outlier)")
    fig2 = px.box(df_filtered, x='Tempo_di_Stock_Giorni', y='Linea', color='Linea', orientation='h', template='plotly_dark')
    fig2.update_layout(margin=dict(l=0, r=0, t=0, b=0), showlegend=False, separators=",.")
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# MATRICE HEATMAP
st.subheader("Matrice Produttore vs Stagione (Giorni Medi di Stock)")
if not df_filtered.empty:
    pivot_df = pd.pivot_table(df_filtered, values='Tempo_di_Stock_Giorni', index='Produttore', columns='Stagione', aggfunc='mean').fillna(0)
    
    st.write("Puoi ordinare e scorrere la tabella. I colori caldi (rosso) indicano giacenze molto lunghe.")
    
    # Usiamo lo style di pandas per colorare le celle come una heatmap
    styled_df = pivot_df.style.background_gradient(cmap='RdYlGn_r', axis=None).format(lambda x: format_it(x, 1))
    
    st.dataframe(styled_df, use_container_width=True, height=600)
else:
    st.info("Nessun dato disponibile per i filtri selezionati.")

st.markdown("---")


