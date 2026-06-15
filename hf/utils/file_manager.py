import os
import zipfile
import pandas as pd
from datetime import datetime

def package_data(df):
    if df is None or len(df) == 0: return None
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    zip_path = f"Youtube_Export_{ts}.zip"
    csv_path = "youtube_subs.csv"
    
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.write(csv_path)
    
    if os.path.exists(csv_path):
        os.remove(csv_path)
    return zip_path