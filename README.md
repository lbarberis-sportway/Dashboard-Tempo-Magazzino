# Dashboard Tempo di Stock Magazzino 📦

Una dashboard interattiva creata in Python con **Streamlit** per l'analisi dei tempi di giacenza della merce in magazzino. L'applicazione incrocia i dati di Entrata e Uscita applicando una logica **FIFO** (First-In, First-Out) per calcolare il tempo esatto di permanenza in magazzino per ogni articolo, aiutando a identificare inefficienze, stagionalità e performance dei produttori.

## 🌟 Funzionalità Principali

- **Calcolo Logico FIFO:** Accoppia in automatico gli arrivi con le spedizioni in base ai codici a barre, determinando esattamente i giorni di sosta per ogni singolo pacco.
- **Filtri Dinamici Multiselezione:** Permette di analizzare i dati filtrando contemporaneamente per Range di Date, Categoria, Linea, Stagione e Produttore.
- **KPI Riepilogativi:** Visualizzazione immediata di Metriche chiave come il Tempo Medio di Giacenza e i Volumi movimentati.
- **Analisi per Categoria (Bar Chart):** Scopri rapidamente quali sono le categorie di prodotto che rimangono più a lungo a prendere polvere.
- **Distribuzione Outlier (Box-Plot):** Evidenzia dispersioni e picchi anomali di giacenza per ogni Linea di prodotto.
- **Heatmap Produttori vs Stagioni:** Una tabella termica interattiva per incrociare le performance dei fornitori in base alle collezioni/stagionalità.

## 🛠️ Tecnologie Utilizzate

- **Python 3**
- **Streamlit** (Interfaccia Grafica e Web App)
- **Pandas** (Elaborazione Dati e Logica FIFO)
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
   Assicurati di inserire i tuoi due file Excel nella cartella principale del progetto, nominandoli:
   - `ENTRATE MAGAZZINO.xlsx`
   - `USCITE MAGAZZINO.xlsx`
   *(Nota: i file Excel originali sono esclusi dalla repository per motivi di privacy)*

4. **Avvia l'applicazione:**
   ```bash
   streamlit run app.py
   ```
   L'applicazione si aprirà nel tuo browser all'indirizzo `http://localhost:8501`.

## 📁 Struttura del Progetto

- `app.py`: File principale che renderizza l'interfaccia utente in Streamlit.
- `data_loader.py`: Motore logico in background che si occupa di pulire i dati e applicare l'algoritmo FIFO.
- `requirements.txt`: Elenco delle librerie Python necessarie.
- `logo.png`: Favicon dell'applicazione.

## 📝 Licenza
Questo progetto è sviluppato per uso interno/analisi dati.
