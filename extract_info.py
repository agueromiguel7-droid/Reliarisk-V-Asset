import subprocess
import sys
import os

print("Installing required packages...")
subprocess.run([sys.executable, "-m", "pip", "install", "python-docx", "pandas", "openpyxl"], check=True)

try:
    import pandas as pd
    excel_path = r"BD_Campos_San-Tome.xlsx"
    print("\n--- EXCEL SCHEMA ---")
    df = pd.read_excel(excel_path)
    print(df.info())
    print("\n--- EXCEL HEAD ---")
    print(df.head())
except Exception as e:
    print(f"Error reading Excel: {e}")

try:
    import docx
    docx_path = r"Especificaciones Técnicas para Google Antigravity.docx"
    print("\n--- DOCX CONTENT ---")
    doc = docx.Document(docx_path)
    for p in doc.paragraphs:
        if p.text.strip():
            print(p.text)
except Exception as e:
    print(f"Error reading Docx: {e}")
