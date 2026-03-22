import pandas as pd
df = pd.read_excel(r"d:\3_Trabajo\67_C2Core\Campos en Venezuela\BD_Campos_San-Tome.xlsx", header=2)
print("COLUMNS:")
for col in df.columns:
    print(f"- {col}")
