# src/savings.py

def estimate_monthly_savings(df_forecast):
    """
    Estimate monthly savings based on current vs optimized cost.
    Assumes df_forecast contains 1 week of data.
    """
    daily_savings = df_forecast['savings_usd'].sum() / 7  # avg daily savings
    monthly_savings = daily_savings * 30
    return monthly_savings

