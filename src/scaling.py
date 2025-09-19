# src/scaling.py

from constants.config import TARGET_CPU

class Scaler:
    @staticmethod
    def recommend_hosts(cpu_usage_pct, num_hosts, target_cpu=TARGET_CPU):
        """
        Suggest host scaling based on CPU % vs target
        """
        suggested_hosts = max(1, int(num_hosts * (cpu_usage_pct / target_cpu)))
        return suggested_hosts
