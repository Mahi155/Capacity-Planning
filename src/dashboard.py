import streamlit as st
import plotly.graph_objects as go
from src.forecasting import Forecaster
from src.scaling import Scaler
from src.cost import calculate_cost, estimate_monthly_savings
from src.ai_recommendation import generate_recommendation
from openai import OpenAI


class Dashboard:
    def __init__(self, df):
        self.df = df
        self.forecaster = Forecaster(periods=24*60*7)  # 1 week forecast

    def run(self):
        st.title("Multi-Tenant Service Scaling & Cost Optimization Dashboard")

        # -----------------------------
        # Sidebar: API Key
        # -----------------------------
        st.sidebar.subheader("🔑 API Configuration")
        user_api_key = st.sidebar.text_input("Enter your OpenAI API key", type="password")
        client = None
        if user_api_key:
            client = OpenAI(api_key=user_api_key)

        # -----------------------------
        # Filters
        # -----------------------------
        client_option = st.selectbox("Select Client", self.df['client_id'].unique())
        service_option = st.selectbox(
            "Select Service",
            self.df[self.df['client_id'] == client_option]['service_name'].unique()
        )
        region_option = st.selectbox(
            "Select Region",
            self.df[
                (self.df['client_id'] == client_option) &
                (self.df['service_name'] == service_option)
            ]['region'].unique()
        )

        df_filtered = self.df[
            (self.df['client_id'] == client_option) &
            (self.df['service_name'] == service_option) &
            (self.df['region'] == region_option)
        ]

        # -----------------------------
        # Observed Requests & CPU Usage
        # -----------------------------
        st.subheader(f"Observed Requests & CPU Usage ({client_option})")
        fig_obs = go.Figure()
        fig_obs.add_trace(go.Scatter(
            x=df_filtered['timestamp'], y=df_filtered['requests_per_min'],
            name='Requests', yaxis='y1'
        ))
        fig_obs.add_trace(go.Scatter(
            x=df_filtered['timestamp'], y=df_filtered['cpu_usage_pct'],
            name='CPU Usage %', yaxis='y2'
        ))
        fig_obs.update_layout(
            xaxis_title='Timestamp',
            yaxis=dict(title='Requests', side='left'),
            yaxis2=dict(title='CPU %', overlaying='y', side='right'),
            legend=dict(x=0, y=1.2)
        )
        st.plotly_chart(fig_obs, use_container_width=True)

        # -----------------------------
        # Forecast & Scaling Recommendation
        # -----------------------------
        st.subheader("Forecast & Scaling Recommendation")
        forecast_df = self.forecaster.forecast_service(df_filtered)

        # Merge forecast into existing df
        df_forecast = df_filtered.copy()
        df_forecast = df_forecast.merge(
            forecast_df[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].rename(columns={'ds': 'timestamp'}),
            on='timestamp', how='left'
        )
        df_forecast['recommended_hosts'] = df_forecast.apply(
            lambda r: Scaler.recommend_hosts(r['cpu_usage_pct'], r['num_hosts']), axis=1
        )
        df_forecast['current_cost'] = df_forecast.apply(
            lambda r: calculate_cost(r['num_hosts'], r['instance_type']), axis=1
        )
        df_forecast['optimized_cost'] = df_forecast.apply(
            lambda r: calculate_cost(r['recommended_hosts'], r['instance_type']), axis=1
        )
        df_forecast['savings_usd'] = df_forecast['current_cost'] - df_forecast['optimized_cost']

        # -----------------------------
        # Forecast Plot with Confidence Interval
        # -----------------------------
        fig_forecast = go.Figure()
        fig_forecast.add_trace(go.Scatter(
            x=df_forecast['timestamp'], y=df_forecast['yhat'],
            mode='lines', name='Forecast Requests'
        ))
        fig_forecast.add_trace(go.Scatter(
            x=df_forecast['timestamp'], y=df_forecast['yhat_upper'],
            mode='lines', name='Upper Bound', line=dict(dash='dot')
        ))
        fig_forecast.add_trace(go.Scatter(
            x=df_forecast['timestamp'], y=df_forecast['yhat_lower'],
            mode='lines', name='Lower Bound', line=dict(dash='dot'),
            fill='tonexty', fillcolor='rgba(0,100,80,0.2)'
        ))
        st.plotly_chart(fig_forecast, use_container_width=True)

        # -----------------------------
        # Data Table & Monthly Savings
        # -----------------------------
        st.dataframe(df_forecast[['timestamp', 'requests_per_min', 'yhat',
                                  'num_hosts', 'recommended_hosts', 'current_cost',
                                  'optimized_cost', 'savings_usd']].head(10))

        monthly_savings = estimate_monthly_savings(df_forecast)
        st.metric(label="Estimated Monthly Savings", value=f"${monthly_savings:,.2f}")

        # -----------------------------
        # Additional Forecast/Scaling Graphs
        # -----------------------------
        st.subheader("Scaling & Cost Visualizations")

        # Requests vs Forecast
        fig_req = go.Figure()
        fig_req.add_trace(go.Scatter(x=df_forecast['timestamp'], y=df_forecast['requests_per_min'],
                                     name='Observed Requests'))
        fig_req.add_trace(go.Scatter(x=df_forecast['timestamp'], y=df_forecast['yhat'],
                                     name='Forecast Requests'))
        st.plotly_chart(fig_req, use_container_width=True)

        # Current Hosts vs Recommended Hosts
        fig_hosts = go.Figure()
        fig_hosts.add_trace(go.Scatter(x=df_forecast['timestamp'], y=df_forecast['num_hosts'],
                                       name='Current Hosts'))
        fig_hosts.add_trace(go.Scatter(x=df_forecast['timestamp'], y=df_forecast['recommended_hosts'],
                                       name='Recommended Hosts'))
        st.plotly_chart(fig_hosts, use_container_width=True)

        # Current Cost vs Optimized Cost
        fig_cost = go.Figure()
        fig_cost.add_trace(go.Scatter(x=df_forecast['timestamp'], y=df_forecast['current_cost'],
                                      name='Current Cost'))
        fig_cost.add_trace(go.Scatter(x=df_forecast['timestamp'], y=df_forecast['optimized_cost'],
                                      name='Optimized Cost'))
        st.plotly_chart(fig_cost, use_container_width=True)

        # -----------------------------
        # AI Recommendations
        # -----------------------------
        st.subheader("AI Recommendations")

        if client:
            try:
                rec_text = generate_recommendation(
                    client=client,
                    df_forecast=df_forecast,
                    client_id=client_option,
                    service_name=service_option,
                    region=region_option
                )
                st.write(rec_text)
            except Exception as e:
                st.error(f"Error generating recommendation: {e}")
        else:
            st.info("Enter your OpenAI API key in the sidebar to enable AI recommendations.")
