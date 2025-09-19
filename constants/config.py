# constants/config.py

INSTANCE_COST = {
    'm5.large': 100,  # USD per hour
    # Add more instance types here
}

TARGET_CPU = 90  # CPU % target for scaling
# Forecast horizon in minutes
FORECAST_PERIODS = 60 * 24  # 1 day forecast

