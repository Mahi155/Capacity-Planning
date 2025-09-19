````markdown
# CapacityPlanning

## Overview
CapacityPlanning is a multi-tenant service scaling and cost optimization dashboard. It allows users to:

- Visualize requests and CPU usage per service and region.
- Forecast future requests using Prophet with trend and seasonality.
- Get scaling recommendations based on CPU usage.
- Calculate current and optimized costs, and estimated monthly savings.
- Generate AI-driven recommendations for optimization.

## Featuress
- Minute-level synthetic or uploaded CSV data.
- Interactive plots with Plotly (dual y-axis for requests and CPU usage).
- Forecast with confidence intervals.
- Cost and savings calculation.
- Multi-tenant support (clients, services, regions).

## Setup

### Requirements
Install dependencies using pip:

```bash
pip install -r requirements.txt
````

### Run Dashboard

```bash
streamlit run main.py
```

* Use synthetic data (default) or upload your own CSV.
* Select client, service, and region from the sidebar.
* Explore visualizations, forecasts, scaling recommendations, and estimated savings.

## Project Structure

```
CapacityPlanning/
│
├── README.md
├── setup.py
├── requirements.txt
│
├── constants/
│   └── config.py
│
├── data/
│   └── sample_data.csv
│
├── src/
│   ├── __init__.py
│   ├── data_loader.py
│   ├── forecasting.py
│   ├── scaling.py
│   ├── cost.py
│   ├── dashboard.py
│   └── ai_recommendation.py
│
└── main.py
```

## Notes

* The dashboard uses Plotly for interactive graphs.
* Forecasting is powered by Prophet.
* AI recommendations use OpenAI’s API (requires API key).
* Synthetic data generator produces one week of minute-level traffic per client/service/region.

```
```
