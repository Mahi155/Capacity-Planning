# src/cost.py

INSTANCE_COSTS = {
    "m5.large": 0.096,  # USD per hour
    "t3.medium": 0.0416,
    "c5.large": 0.085
}

def calculate_cost(num_hosts, instance_type):
    """
    Cost per minute = instance hourly cost * num_hosts / 60
    """
    hourly_cost = INSTANCE_COSTS.get(instance_type, 0.1)
    return num_hosts * hourly_cost / 60  # per-minute cost

def estimate_monthly_savings(df_forecast):
    """
    Estimate monthly savings based on 1-week data.
    """
    weekly_savings = df_forecast['savings_usd'].sum()
    return weekly_savings * 4  # approximate month
