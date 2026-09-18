"""Small helpers shared by the Flask application and its checks."""
from pathlib import Path
import numpy as np
import pandas as pd
import joblib

ROOT = Path(__file__).resolve().parent
model = joblib.load(ROOT / 'model/housing_model.joblib')

def predict_price(values):
    row = dict(values)
    if row.get('suburb') not in ['Parramatta', 'Blacktown', 'Mosman']:
        raise ValueError('Choose a supported suburb.')
    if row.get('property_type') not in ['Apartment', 'House', 'Townhouse']:
        raise ValueError('Choose a supported property type.')
    for key, low, high in [('bedrooms', 0, 7), ('bathrooms', 1, 5), ('parking', 0, 6)]:
        value = row.get(key)
        if key == 'parking' and value in ['', None]:
            row[key] = np.nan
            continue
        try:
            value = float(value)
        except (ValueError, TypeError):
            raise ValueError('Enter a valid number for ' + key)
        if not np.isfinite(value) or not value.is_integer() or not low <= value <= high:
            raise ValueError(key + ' is outside the supported range.')
        row[key] = value
    try:
        date = pd.to_datetime(row['sale_date'], format='%Y-%m-%d')
        if pd.isna(date):
            raise ValueError('Date is missing.')
    except (ValueError, KeyError, TypeError):
        raise ValueError('Enter a valid date.')
    row['sale_month'] = (date.year - 2025) * 12 + date.month - 1
    row['bathrooms_per_bedroom'] = row['bathrooms'] / max(row['bedrooms'], 1)
    return float(model.predict(pd.DataFrame([row]))[0])
