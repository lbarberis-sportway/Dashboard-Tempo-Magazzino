import pandas as pd
import sys

file_path = r"C:\Users\Vstor\Desktop\Ludovico\Analisi Dati\Dashboard-Tempo-Magazzino\VENDITE.xlsx"
try:
    df = pd.read_excel(file_path, nrows=5)
    print("Colonne VENDITE:", list(df.columns))
except Exception as e:
    print("Errore:", e)
