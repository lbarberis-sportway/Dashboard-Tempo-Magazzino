# Dashboard Tempo di Stock & Ciclo di Vita Magazzino 📦

Una dashboard interattiva creata in Python con **Streamlit** per l'analisi completa dei tempi di giacenza della merce, dall'ingresso in magazzino centrale fino alla vendita finale in negozio. L'applicazione incrocia i dati logistici e di cassa applicando una logica **FIFO a cascata** (First-In, First-Out) per calcolare il tempo esatto del ciclo di vita per ogni articolo.

## 🌟 Funzionalità Principali

- **Calcolo Logico FIFO a Cascata:** Accoppia in automatico gli arrivi dal fornitore con le spedizioni ai negozi, e infine con lo scontrino emesso, determinando:
  - *Tempo di Magazzino:* Giorni di attesa nel polo logistico.
  - *Tempo di Scaffale:* Giorni di permanenza nel punto vendita prima dell'acquisto.
  - *Lead Time Totale:* Il ciclo di vita completo del prodotto.
- **Filtri Dinamici Multiselezione:** Permette di analizzare i dati filtrando per Periodo, Negozio, Categoria, Linea, Stagione e Produttore.
- **KPI Riepilogativi:** Visualizzazione immediata di metriche chiave per individuare dove la merce è più lenta (Magazzino vs Scaffale).
- **Analisi Comparativa (Stacked Bar Charts):** Grafici a barre bicolore per "Top Linee" e "Top Produttori" che separano visivamente il tempo perso in magazzino da quello perso in negozio.
- **Heatmap delle Performance (Matrici):** Tabelle termiche interattive con sfondo "intelligente" per incrociare le performance dei Negozi per:
  - *Categoria*
  - *Linea*
  - *Produttore*

## 🛠️ Tecnologie Utilizzate

- **Python 3**
- **Streamlit** (Interfaccia Grafica e Web App)
- **Pandas** (Elaborazione Dati e logica FIFO avanzata)
- **Plotly** (Grafici interattivi)
- **OpenPyXL** (Lettura file Excel)

## 🚀 Installazione e Avvio Locale

1. **Clona la repository:**
   ```bash
   git clone https://github.com/TUO_USERNAME/Dashboard-Tempo-Magazzino.git
   cd Dashboard-Tempo-Magazzino
   ```

2. **Installa le dipendenze:**
   È consigliato utilizzare un ambiente virtuale (venv).
   ```bash
   pip install -r requirements.txt
   ```

3. **Inserisci i dati:**
   Assicurati di inserire i tuoi file Excel nella cartella principale del progetto, nominandoli esattamente:
   - `ENTRATE MAGAZZINO.xlsx`
   - `USCITE MAGAZZINO.xlsx`
   - `VENDITE.xlsx` *(Opzionale: se presente abiliterà il calcolo del Tempo di Scaffale)*
   *(Nota: i file Excel originali non devono essere committati per motivi di privacy)*

4. **Avvia l'applicazione:**
   ```bash
   streamlit run app.py
   ```
   L'applicazione si aprirà nel tuo browser all'indirizzo `http://localhost:8501`.

## 📁 Struttura del Progetto

- `app.py`: File principale che renderizza l'interfaccia utente, i grafici e i filtri in Streamlit.
- `data_loader.py`: Motore logico in background che si occupa di pulire i dati e applicare il doppio algoritmo FIFO per calcolare le metriche storiche.
- `requirements.txt`: Elenco delle librerie Python necessarie.
- `logo.png`: Favicon dell'applicazione.

## 📝 Licenza
Questo progetto è sviluppato per uso interno/analisi dati logistici.
