from pathlib import Path

import pandas as pd


def preprocess_raw_data(raw_data_full_path: Path, processed_data_dir: Path):
    df = pd.read_csv(raw_data_full_path)
    print(df.head())


if __name__ == '__main__':
    base_dir = Path(__file__).resolve().parent.parent
    raw_data_full_path = base_dir / 'data' / 'raw' / 'admission.csv'
    processed_data_dir = base_dir / 'data' / 'processed'
    preprocess_raw_data(raw_data_full_path, processed_data_dir)
