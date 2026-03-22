import pandas as pd
import docx

with open(r"d:\3_Trabajo\67_C2Core\Campos en Venezuela\extracted_output.txt", "w", encoding="utf-8") as f:
    try:
        excel_path = r"d:\3_Trabajo\67_C2Core\Campos en Venezuela\BD_Campos_San-Tome.xlsx"
        f.write("\n--- EXCEL SCHEMA ---\n")
        df = pd.read_excel(excel_path)
        
        import io
        buf = io.StringIO()
        df.info(buf=buf)
        f.write(buf.getvalue())
        
        f.write("\n--- EXCEL HEAD ---\n")
        f.write(df.head().to_string())
    except Exception as e:
        f.write(f"Error reading Excel: {e}\n")

    try:
        docx_path = r"d:\3_Trabajo\67_C2Core\Campos en Venezuela\Especificaciones Técnicas para Google Antigravity.docx"
        f.write("\n--- DOCX CONTENT ---\n")
        doc = docx.Document(docx_path)
        for p in doc.paragraphs:
            if p.text.strip():
                f.write(p.text + "\n")
    except Exception as e:
        f.write(f"Error reading Docx: {e}\n")
