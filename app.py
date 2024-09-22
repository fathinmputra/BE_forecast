# app.py
from flask import Flask, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
from datetime import date, timedelta
from flask_cors import CORS
from config import Config
from models import db, PriceData

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)  # Enable CORS for frontend requests

db.init_app(app)


@app.route('/forecast', methods=['GET'])
def forecast():
    # Mengambil seluruh data dari tabel 'prices' hingga hari ini
    today = date.today()
    data = PriceData.query.filter(PriceData.date <= today).all()

    if not data:
        return jsonify({"error": "No data available"}), 404

    # Konversi data ke DataFrame pandas
    df = pd.DataFrame([(d.date, d.price)
                      for d in data], columns=["Tanggal", "Harga"])
    df.set_index('Tanggal', inplace=True)
    df = df.asfreq('D')  # Menetapkan frekuensi harian pada DataFrame

    # Cek stasioneritas menggunakan uji ADF (Augmented Dickey-Fuller)
    result = adfuller(df['Harga'].dropna())
    if result[1] > 0.05:
        df['Harga'] = df['Harga'].ffill()  # Forward fill jika tidak stasioner

    # Fit ARIMA model menggunakan seluruh data historis
    try:
        model = ARIMA(df['Harga'], order=(1, 1, 1))
        model_fit = model.fit()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Forecasting untuk 3 hari ke depan
    forecast_steps = 3
    forecast = model_fit.forecast(steps=forecast_steps)
    forecast_index = pd.date_range(
        start=today + timedelta(days=1), periods=forecast_steps, freq='D')

    # Buat DataFrame untuk hasil forecast
    forecast_df = pd.DataFrame({
        'Tanggal': forecast_index,
        'Harga': forecast
    })

    # Ambil 4 data actual terakhir (termasuk hari ini)
    last_4_actual = df.tail(4).reset_index()

    # Gabungkan data actual terakhir dan forecast
    combined_df = pd.concat([last_4_actual, forecast_df], ignore_index=True)

    # Tandai data actual dan data forecast
    combined_df['Data'] = ['Actual'] * \
        len(last_4_actual) + ['Forecast'] * len(forecast_df)

    # Mengubah DataFrame gabungan ke format JSON
    result = {
        "actual_data": combined_df[combined_df['Data'] == 'Actual'][['Tanggal', 'Harga']].to_dict(orient='records'),
        "forecast_data": combined_df[combined_df['Data'] == 'Forecast'][['Tanggal', 'Harga']].to_dict(orient='records')
    }

    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
