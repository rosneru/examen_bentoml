from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

FEATURE_NAMES = [
    'GRE Score',
    'TOEFL Score',
    'University Rating',
    'SOP',
    'LOR',
    'CGPA',
    'Research',
]

TARGET = 'Chance of Admit'


def preprocess_raw_data(raw_data_full_path: Path, processed_data_dir: Path):
    df = pd.read_csv(raw_data_full_path)
    df.columns = df.columns.str.strip()

    features = df[FEATURE_NAMES]
    target = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        features, target, test_size=0.3, random_state=42
    )

    X_train.to_csv(processed_data_dir / 'X_train.csv', index=False)
    X_test.to_csv(processed_data_dir / 'X_test.csv', index=False)
    y_train.to_csv(processed_data_dir / 'y_train.csv', index=False)
    y_test.to_csv(processed_data_dir / 'y_test.csv', index=False)


if __name__ == '__main__':
    base_dir = Path(__file__).resolve().parent.parent
    raw_data_full_path = base_dir / 'data' / 'raw' / 'admission.csv'
    processed_data_dir = base_dir / 'data' / 'processed'
    preprocess_raw_data(raw_data_full_path, processed_data_dir)
