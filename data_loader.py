import pandas as pd
import streamlit as st

@st.cache_data
def load_and_process_data(entrate_path, uscite_path):
    # Caricamento dei file
    df_entrate = pd.read_excel(entrate_path)
    df_uscite = pd.read_excel(uscite_path)
    
    # Pulizia nomi colonne
    df_entrate.columns = df_entrate.columns.str.strip()
    df_uscite.columns = df_uscite.columns.str.strip()
    
    # Gestione problemi di codifica e uniformità colonne Quantità
    for df in [df_entrate, df_uscite]:
        for col in df.columns:
            if 'Quantit' in col:
                df.rename(columns={col: 'Quantita'}, inplace=True)
                break
                
    # Conversione Date
    df_entrate['Data'] = pd.to_datetime(df_entrate['Data'])
    df_uscite['Data'] = pd.to_datetime(df_uscite['Data'])
    
    # Ordinamento cronologico
    df_entrate = df_entrate.sort_values(by='Data').reset_index(drop=True)
    df_uscite = df_uscite.sort_values(by='Data').reset_index(drop=True)
    
    # Rimuovi record senza Barcode o Quantita invalide
    df_entrate = df_entrate.dropna(subset=['Barcode', 'Quantita'])
    df_uscite = df_uscite.dropna(subset=['Barcode', 'Quantita'])
    
    # Calcolo Logica FIFO per determinare il Tempo di Stock
    # Creiamo un dizionario di code (liste) per ogni Barcode in entrata
    # Ogni elemento nella coda è un dizionario: {'Data_Entrata': datetime, 'Quantita_Disponibile': float}
    
    entrate_dict = {}
    for idx, row in df_entrate.iterrows():
        barcode = row['Barcode']
        if barcode not in entrate_dict:
            entrate_dict[barcode] = []
        entrate_dict[barcode].append({
            'Data_Entrata': row['Data'],
            'Quantita_Disponibile': row['Quantita'],
            'Categoria': row.get('Categoria', 'N/D'),
            'Linea': row.get('Linea', 'N/D'),
            'Stagione': row.get('Stagione', 'N/D'),
            'Produttore': row.get('Produttore', 'N/D'),
            'Articolo': row.get('Articolo / Prodotto', 'N/D')
        })
        
    matched_records = []
    
    for idx, row in df_uscite.iterrows():
        barcode = row['Barcode']
        qta_uscita = row['Quantita']
        data_uscita = row['Data']
        
        if barcode in entrate_dict:
            queue = entrate_dict[barcode]
            while qta_uscita > 0 and queue:
                entrata = queue[0] # Prendi il lotto più vecchio
                
                if entrata['Data_Entrata'] > data_uscita:
                    # Anomalia: Merce in uscita con data precedente all'entrata
                    # Consideriamo come tempo stock 0 per evitare giorni negativi,
                    # o semplicemente matchamo lo stesso.
                    pass
                
                qta_da_scalare = min(qta_uscita, entrata['Quantita_Disponibile'])
                
                # Registriamo il match
                matched_records.append({
                    'Barcode': barcode,
                    'Articolo': entrata['Articolo'],
                    'Categoria': entrata['Categoria'],
                    'Linea': entrata['Linea'],
                    'Stagione': entrata['Stagione'],
                    'Produttore': entrata['Produttore'],
                    'Data_Entrata': entrata['Data_Entrata'],
                    'Data_Uscita': data_uscita,
                    'Quantita': qta_da_scalare,
                    'Tempo_di_Stock_Giorni': max((data_uscita - entrata['Data_Entrata']).days, 0)
                })
                
                qta_uscita -= qta_da_scalare
                entrata['Quantita_Disponibile'] -= qta_da_scalare
                
                if entrata['Quantita_Disponibile'] <= 0:
                    queue.pop(0) # Rimuovi il lotto se esaurito
                    
    df_matched = pd.DataFrame(matched_records)
    
    return df_entrate, df_uscite, df_matched
