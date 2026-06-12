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
VENDITE_PATH = "VENDITE.xlsx"

try:
    with st.spinner("Caricamento ed elaborazione dati in corso (FIFO)..."):
        import os
        if os.path.exists(VENDITE_PATH):
            df_entrate, df_uscite, df_matched = load_and_process_data(ENTRATE_PATH, USCITE_PATH, VENDITE_PATH)
        else:
            df_entrate, df_uscite, df_matched = load_and_process_data(ENTRATE_PATH, USCITE_PATH)
except Exception as e:
    st.error(f"Errore durante il caricamento dei dati: {e}")
    st.stop()

if df_matched.empty:
    st.warning("Nessuna corrispondenza trovata con i dati attuali.")
    st.stop()

has_vendite = 'Tempo_di_Scaffale_Giorni' in df_matched.columns

# SIDEBAR - Filtri
st.sidebar.header("Filtri di Analisi")

# Filtro Data
if has_vendite:
    date_col = 'Data_Vendita'
else:
    date_col = 'Data_Uscita'

min_date = df_matched[date_col].min().date()
max_date = df_matched[date_col].max().date()
date_range = st.sidebar.date_input("Periodo di Analisi", [min_date, max_date], min_value=min_date, max_value=max_date)

# Filtri Multipli
def get_unique(df, col):
    if col in df.columns:
        return sorted([str(x) for x in df[col].unique() if pd.notna(x)])
    return []

sel_negozio = []
if has_vendite:
    sel_negozio = st.sidebar.multiselect("Negozio", get_unique(df_matched, 'Negozio'), default=[])
sel_categoria = st.sidebar.multiselect("Categoria", get_unique(df_matched, 'Categoria'), default=[])
sel_linea = st.sidebar.multiselect("Linea", get_unique(df_matched, 'Linea'), default=[])
sel_stagione = st.sidebar.multiselect("Stagione", get_unique(df_matched, 'Stagione'), default=[])
sel_produttore = st.sidebar.multiselect("Produttore", get_unique(df_matched, 'Produttore'), default=[])

st.sidebar.info("💡 Lascia il campo vuoto per includere tutti i valori.")

# Applicazione Filtri
df_filtered = df_matched.copy()

if len(date_range) == 2:
    start_date, end_date = date_range
    df_filtered = df_filtered[(df_filtered[date_col].dt.date >= start_date) & (df_filtered[date_col].dt.date <= end_date)]

if has_vendite and sel_negozio:
    df_filtered = df_filtered[df_filtered['Negozio'].isin(sel_negozio)]
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

if has_vendite:
    tempo_medio = df_filtered['Lead_Time_Totale_Giorni'].mean()
    tempo_scaffale = df_filtered['Tempo_di_Scaffale_Giorni'].mean()
    tempo_magazzino = df_filtered['Tempo_di_Stock_Giorni'].mean()
    tot_qta = df_filtered['Quantita'].sum()
    
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{format_it(tempo_magazzino, 1)} gg</div><div class="metric-label">Tempo Medio Magazzino</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{format_it(tempo_scaffale, 1)} gg</div><div class="metric-label">Tempo Medio Scaffale</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{format_it(tempo_medio, 1)} gg</div><div class="metric-label">Lead Time Totale Medio</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{format_it(tot_qta)}</div><div class="metric-label">Unità Vendute</div></div>', unsafe_allow_html=True)
else:
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
if has_vendite:
    st.subheader("Tempo Medio per Categoria (Magazzino vs Scaffale)")
    st.info("Classifica delle Categorie in base al Lead Time Totale. La barra è divisa tra Magazzino (Blu) e Negozio (Arancione).")
    
    df_cat = df_filtered.groupby('Categoria')[['Tempo_di_Stock_Giorni', 'Tempo_di_Scaffale_Giorni', 'Lead_Time_Totale_Giorni']].mean().reset_index()
    df_cat = df_cat.nlargest(20, 'Lead_Time_Totale_Giorni').sort_values('Lead_Time_Totale_Giorni', ascending=True)
    
    fig_stack = go.Figure()
    fig_stack.add_trace(go.Bar(
        y=df_cat['Categoria'], x=df_cat['Tempo_di_Stock_Giorni'], name='Magazzino', orientation='h', marker_color='#3b82f6'
    ))
    fig_stack.add_trace(go.Bar(
        y=df_cat['Categoria'], x=df_cat['Tempo_di_Scaffale_Giorni'], name='Scaffale', orientation='h', marker_color='#f97316'
    ))
    fig_stack.update_layout(barmode='stack', template='plotly_dark', margin=dict(l=0, r=0, t=30, b=0), separators=",.")
    st.plotly_chart(fig_stack, use_container_width=True)
    
    st.markdown("---")
    
    colA, colB = st.columns(2)
    with colA:
        st.subheader("Tempo Medio per Linea")
        df_linea = df_filtered.groupby('Linea')[['Tempo_di_Stock_Giorni', 'Tempo_di_Scaffale_Giorni', 'Lead_Time_Totale_Giorni']].mean().reset_index()
        df_linea = df_linea.nlargest(15, 'Lead_Time_Totale_Giorni').sort_values('Lead_Time_Totale_Giorni', ascending=True)
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(y=df_linea['Linea'], x=df_linea['Tempo_di_Stock_Giorni'], name='Magazzino', orientation='h', marker_color='#3b82f6'))
        fig2.add_trace(go.Bar(y=df_linea['Linea'], x=df_linea['Tempo_di_Scaffale_Giorni'], name='Scaffale', orientation='h', marker_color='#f97316'))
        fig2.update_layout(barmode='stack', template='plotly_dark', margin=dict(l=0, r=0, t=30, b=0), separators=",.", showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)
        
    with colB:
        st.subheader("Tempo Medio per Produttore")
        df_prod = df_filtered.groupby('Produttore')[['Tempo_di_Stock_Giorni', 'Tempo_di_Scaffale_Giorni', 'Lead_Time_Totale_Giorni']].mean().reset_index()
        df_prod = df_prod.nlargest(15, 'Lead_Time_Totale_Giorni').sort_values('Lead_Time_Totale_Giorni', ascending=True)
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(y=df_prod['Produttore'], x=df_prod['Tempo_di_Stock_Giorni'], name='Magazzino', orientation='h', marker_color='#3b82f6'))
        fig3.add_trace(go.Bar(y=df_prod['Produttore'], x=df_prod['Tempo_di_Scaffale_Giorni'], name='Scaffale', orientation='h', marker_color='#f97316'))
        fig3.update_layout(barmode='stack', template='plotly_dark', margin=dict(l=0, r=0, t=30, b=0), separators=",.", showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)
        
    st.markdown("---")
    
    st.subheader("Matrice Categoria vs Negozio (Giorni Medi a Scaffale)")
    if not df_filtered.empty:
        # Non usiamo fillna(0) così i dati mancanti restano NaN
        pivot_df = pd.pivot_table(df_filtered, values='Tempo_di_Scaffale_Giorni', index='Categoria', columns='Negozio', aggfunc='mean')
        st.write("Puoi ordinare e scorrere la tabella. I colori caldi (rosso) indicano giacenze molto lunghe. Le celle nere/scure indicano che non c'è stato alcun incrocio/vendita.")
        
        # Applichiamo il gradiente solo ai valori validi, i NaN avranno lo sfondo nero
        styled_df = (pivot_df.style
            .background_gradient(cmap='RdYlGn_r', axis=None)
            .highlight_null(color='#111111')
            .format(lambda x: format_it(x, 1) if pd.notna(x) else "-")
        )
        st.dataframe(styled_df, use_container_width=True, height=600)
    else:
        st.info("Nessun dato disponibile.")

    st.markdown("---")
    
    st.subheader("Matrice Linea vs Negozio (Giorni Medi a Scaffale)")
    if not df_filtered.empty:
        pivot_df2 = pd.pivot_table(df_filtered, values='Tempo_di_Scaffale_Giorni', index='Linea', columns='Negozio', aggfunc='mean')
        styled_df2 = (pivot_df2.style
            .background_gradient(cmap='RdYlGn_r', axis=None)
            .highlight_null(color='#111111')
            .format(lambda x: format_it(x, 1) if pd.notna(x) else "-")
        )
        st.dataframe(styled_df2, use_container_width=True, height=600)
    else:
        st.info("Nessun dato disponibile.")

    st.markdown("---")
    
    st.subheader("Matrice Produttore vs Negozio (Giorni Medi a Scaffale)")
    if not df_filtered.empty:
        pivot_df3 = pd.pivot_table(df_filtered, values='Tempo_di_Scaffale_Giorni', index='Produttore', columns='Negozio', aggfunc='mean')
        styled_df3 = (pivot_df3.style
            .background_gradient(cmap='RdYlGn_r', axis=None)
            .highlight_null(color='#111111')
            .format(lambda x: format_it(x, 1) if pd.notna(x) else "-")
        )
        st.dataframe(styled_df3, use_container_width=True, height=600)
    else:
        st.info("Nessun dato disponibile.")

else:
    colA, colB = st.columns(2)
    with colA:
        st.subheader("Tempo Medio per Categoria")
        st.info("Top 20 categorie con la giacenza media più lunga.")
        df_cat = df_filtered.groupby('Categoria')['Tempo_di_Stock_Giorni'].mean().nlargest(20).sort_values(ascending=True)
        st.bar_chart(df_cat, horizontal=True)

    with colB:
        st.subheader("Tempo Medio per Produttore")
        df_prod = df_filtered.groupby('Produttore')['Tempo_di_Stock_Giorni'].mean().nlargest(20).sort_values(ascending=True)
        st.bar_chart(df_prod, horizontal=True)

    st.markdown("---")

    st.subheader("🔥 Matrice Produttore vs Stagione (Giorni Medi di Stock)")
    if not df_filtered.empty:
        pivot_df = pd.pivot_table(df_filtered, values='Tempo_di_Stock_Giorni', index='Produttore', columns='Stagione', aggfunc='mean').fillna(0)
        st.write("Puoi ordinare e scorrere la tabella. I colori caldi (rosso) indicano giacenze molto lunghe.")
        styled_df = pivot_df.style.background_gradient(cmap='RdYlGn_r', axis=None).format(lambda x: format_it(x, 1))
        st.dataframe(styled_df, use_container_width=True, height=600)
    else:
        st.info("Nessun dato disponibile per i filtri selezionati.")

st.markdown("---")
