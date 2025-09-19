import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# ------------------------------
# Config
# ------------------------------
NUM_CLIENTS = 3
SERVICES = ['search_api', 'recommendations']
REGIONS = ['us-east-1', 'us-west-2']
DAYS = 7  # generate 1 week of data
INSTANCE_TYPES = ['t3.medium', 'm5.large', 'c5.large']
OUTPUT_CSV = "data/sample_saas_data.csv"

# ------------------------------
# Helper: Sinusoidal traffic
# ------------------------------
def generate_requests(period_minutes=24*60, base=1000, amplitude=800, noise=50, length=None):
    """
    Generate requests per minute with daily sinusoidal pattern + noise
    """
    if length is None:
        length = period_minutes
    t = np.arange(length)
    requests = base + amplitude * np.sin(2 * np.pi * t / period_minutes)
    requests += np.random.normal(0, noise, size=length)
    return np.clip(requests, 0, None).astype(int)

# ------------------------------
# Generate dataset
# ------------------------------
records = []
total_minutes = DAYS * 24 * 60
timestamps = [datetime.now() - timedelta(days=DAYS) + timedelta(minutes=i) for i in range(total_minutes)]

for client_id in range(1, NUM_CLIENTS+1):
    for service in SERVICES:
        for region in REGIONS:
            # Daily sinusoidal requests
            requests = generate_requests(length=total_minutes)

            # Weekly pattern: lower traffic on weekends
            day_of_week = np.array([ts.weekday() for ts in timestamps])
            weekly_factor = np.where(day_of_week < 5, 1.0, 0.6)
            requests = (requests * weekly_factor).astype(int)

            # CPU proportional to requests
            cpu = np.clip(30 + (requests / max(requests)) * 60 + np.random.normal(0, 5, total_minutes), 0, 100)

            # Number of hosts and instance type
            num_hosts = 5 if service == 'recommendations' else 10
            instance_type = np.random.choice(INSTANCE_TYPES)

            # Create records
            for ts, req, c in zip(timestamps, requests, cpu):
                records.append({
                    'client_id': f'client_{client_id}',
                    'service_name': service,
                    'region': region,
                    'timestamp': ts,
                    'requests_per_min': req,
                    'cpu_usage_pct': c,
                    'num_hosts': num_hosts,
                    'instance_type': instance_type
                })

# ------------------------------
# Save to CSV
# ------------------------------
df = pd.DataFrame(records)
df.to_csv(OUTPUT_CSV, index=False)
print(f"✅ Sample dataset saved to {OUTPUT_CSV}")

