# main.py

import streamlit as st
from src.data_loader import DataLoader
from src.dashboard import Dashboard
import pandas as pd

st.set_page_config(page_title="Multi-Tenant Scaling Dashboard", layout="wide")
st.title("Multi-Tenant Service Scaling & Cost Optimization")

# Sidebar options
st.sidebar.header("Data Options")
use_synthetic = st.sidebar.checkbox("Use Synthetic Data", value=True)
uploaded_file = st.sidebar.file_uploader("Upload CSV", type="csv")

# Load data
if uploaded_file is not None:
    try:
        df_uploaded = pd.read_csv(uploaded_file, parse_dates=['timestamp'])
        st.success("CSV loaded successfully!")
    except Exception as e:
        st.error(f"Error loading CSV: {str(e)}")
        df_uploaded = None
else:
    df_uploaded = None

if use_synthetic or df_uploaded is None:
    data_loader = DataLoader()
    df = data_loader.generate_synthetic_data(num_clients=3, days=7)
    st.info("Using synthetic 1-week multi-tenant data for demonstration.")
else:
    df = df_uploaded
    st.info("Using uploaded CSV data.")

# Launch dashboard
dashboard = Dashboard(df)
dashboard.run()
