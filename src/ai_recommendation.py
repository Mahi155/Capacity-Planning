import openai
import os
import pandas as pd

openai.api_key = os.getenv("OPENAI_API_KEY")


def generate_recommendation(df_forecast, client_id, service_name, region):
    """
    Generate AI recommendation for a client-service-region
    using full forecast + observed data with spike/trend detection.
    """
    try:
        # Compute summary metrics
        requests_min = df_forecast['requests_per_min'].min()
        requests_max = df_forecast['requests_per_min'].max()
        requests_mean = df_forecast['requests_per_min'].mean()

        cpu_min = df_forecast['cpu_usage_pct'].min()
        cpu_max = df_forecast['cpu_usage_pct'].max()
        cpu_mean = df_forecast['cpu_usage_pct'].mean()

        current_hosts = int(df_forecast['num_hosts'].max())
        recommended_hosts = int(df_forecast['recommended_hosts'].max())
        savings = df_forecast['savings_usd'].sum()

        # Detect notable spikes
        threshold = requests_mean + 2 * df_forecast['requests_per_min'].std()
        spikes = df_forecast[df_forecast['requests_per_min'] > threshold]
        spike_summary = ""
        if not spikes.empty:
            spike_times = spikes['timestamp'].dt.strftime("%Y-%m-%d %H:%M").tolist()
            spike_summary = f"Notable request spikes at: {', '.join(spike_times[:5])}"  # limit to first 5

        # Detect trends: increasing/decreasing over period
        first_half_mean = df_forecast['requests_per_min'][:len(df_forecast)//2].mean()
        second_half_mean = df_forecast['requests_per_min'][len(df_forecast)//2:].mean()
        trend_summary = "Traffic is stable"
        if second_half_mean > first_half_mean * 1.1:
            trend_summary = "Traffic is trending upwards"
        elif second_half_mean < first_half_mean * 0.9:
            trend_summary = "Traffic is trending downwards"

        # Build prompt
        prompt = f"""
                    You are a cloud infrastructure expert. Analyze the following service metrics
                    and suggest optimization opportunities.
                    
                    Client: {client_id}
                    Service: {service_name}
                    Region: {region}
                    
                    Metrics summary (forecast period):
                    - Requests per minute: min={requests_min:.0f}, max={requests_max:.0f}, mean={requests_mean:.0f}
                    - CPU usage %: min={cpu_min:.1f}, max={cpu_max:.1f}, mean={cpu_mean:.1f}
                    - Current hosts: {current_hosts}
                    - Recommended hosts: {recommended_hosts}
                    - Estimated cost savings: ${savings:,.2f}
                    - {trend_summary}
                    - {spike_summary if spike_summary else "No major request spikes detected"}
                    
                    Provide actionable recommendations for:
                    - Scaling strategy
                    - Cost optimization
                    - Performance improvements
                    """

        # Call OpenAI ChatCompletion API (v1.0+)
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a cloud infrastructure expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=350
        )

        recommendation_text = response.choices[0].message.content
        return recommendation_text

    except Exception as e:
        return f"Error generating recommendation: {str(e)}"
