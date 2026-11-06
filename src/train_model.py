from pathlib import Path

import bentoml
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    mean_absolute_error,
    r2_score,
    root_mean_squared_error,
)

MODEL_NAME = 'admission_lr'


def load_split(processed_data_dir: Path):
    X_train = pd.read_csv(processed_data_dir / 'X_train.csv')
    X_test = pd.read_csv(processed_data_dir / 'X_test.csv')
    y_train = pd.read_csv(processed_data_dir / 'y_train.csv').squeeze('columns')
    y_test = pd.read_csv(processed_data_dir / 'y_test.csv').squeeze('columns')
    return X_train, X_test, y_train, y_test


def train(X_train, y_train) -> LinearRegression:
    model = LinearRegression()
    model.fit(X_train, y_train)
    return model


def evaluate(model, X_test, y_test) -> dict[str, float]:
    y_pred = model.predict(X_test)
    return {
        'R2': r2_score(y_test, y_pred),
        'RMSE': root_mean_squared_error(y_test, y_pred),
        'MAE': mean_absolute_error(y_test, y_pred),
    }


def save_model(model, metrics: dict[str, float]) -> bentoml.Model | None:
    if metrics['R2'] >= 0.75:
        model_ref = bentoml.sklearn.save_model(
            MODEL_NAME, model, metadata=metrics
        )
        print(f'Model saved as: {model_ref}')
        return model_ref
    else:
        print('Model *not saved* because performance is not satisfactory.')
        return None


if __name__ == '__main__':
    base_dir = Path(__file__).resolve().parent.parent
    processed_data_dir = base_dir / 'data' / 'processed'

    X_train, X_test, y_train, y_test = load_split(processed_data_dir)

    model = train(X_train, y_train)
    metrics = evaluate(model, X_test, y_test)
    for name, value in metrics.items():
        print(f'{name}: {value:.4f}')

    save_model(model, metrics)
