# src/forecasting.py

import pandas as pd
from prophet import Prophet

class Forecaster:
    def __init__(self, periods=24*60*7, freq='T'):
        """
        periods: number of future periods to forecast (default 1 week of minutes)
        freq: frequency string, e.g., 'T' for minutes
        """
        self.periods = periods
        self.freq = freq

    def forecast_service(self, df):
        """
        Forecast requests for a given service-region-client using Prophet.
        """
        # Prepare dataframe for Prophet
        df_prophet = df[['timestamp', 'requests_per_min']].rename(columns={'timestamp': 'ds', 'requests_per_min': 'y'})
        df_prophet['ds'] = pd.to_datetime(df_prophet['ds'])

        # Fit Prophet model
        model = Prophet(
            daily_seasonality=True,  # captures intra-day pattern
            weekly_seasonality=True,  # captures day-of-week pattern
            yearly_seasonality=False
        )
        model.fit(df_prophet)

        # Create future dataframe
        future = model.make_future_dataframe(periods=self.periods, freq=self.freq)
        forecast = model.predict(future)

        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
