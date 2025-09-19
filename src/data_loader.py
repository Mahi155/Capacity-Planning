# src/data_loader.py

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class DataLoader:
    def __init__(self, filepath=None):
        self.filepath = filepath
        self.df = None

    def load_csv(self):
        if self.filepath:
            self.df = pd.read_csv(self.filepath, parse_dates=['timestamp'])
        return self.df

    @staticmethod
    def generate_synthetic_data(num_clients=3, days=7):
        """
        Generate synthetic minute-level data for multiple clients with daily + weekly seasonality
        """
        np.random.seed(42)
        minutes = pd.date_range(
            start=pd.Timestamp.now() - pd.Timedelta(days=days),
            periods=days * 24 * 60,
            freq='min'  # fixed
        )
        services = ['search_api', 'recommendations']
        regions = ['us-east-1', 'us-west-2']

        data = []
        for client_id in range(1, num_clients + 1):
            for service in services:
                for region in regions:
                    # Daily sinusoidal traffic pattern
                    t = np.arange(len(minutes))
                    daily_pattern = 3000 + 1000 * np.sin(2 * np.pi * t / 1440)
                    weekly_factor = np.where(minutes.dayofweek < 5, 1.0, 0.6)

                    requests = daily_pattern * weekly_factor + np.random.normal(0, 200, len(minutes))
                    requests = np.clip(requests, a_min=0, a_max=None)

                    cpu = np.clip(requests / max(requests) * 70 + np.random.normal(0, 5, len(minutes)), 10, 100)
                    num_hosts = 10 if service == 'search_api' else 5
                    instance_type = 'm5.large'

                    for ts, req, c in zip(minutes, requests, cpu):
                        data.append({
                            'timestamp': ts,
                            'service_name': service,
                            'region': region,
                            'requests_per_min': req,
                            'cpu_usage_pct': c,
                            'num_hosts': num_hosts,
                            'instance_type': instance_type,
                            'client_id': f'client_{client_id}'
                        })
        df = pd.DataFrame(data)
        return df
