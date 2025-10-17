import streamlit as st
import plotly.graph_objects as go
from data_classes import TreasuryData, CpiData, IndexData

st.set_page_config(page_title="Macro Dashboard", layout="wide")
st.title("Interactive Macro & Market Dashboard")

# ------------------- Treasury & Mortgage -------------------
st.header("Treasury & Mortgage Data")
fred_api_key = '3abd82c7d96f863c79848f223a8ef52d'
treasury = TreasuryData(fred_api_key)
treasury.fetch()

# --- EFFR ---
st.subheader("Effective Federal Funds Rate (EFFR)")
fig = go.Figure()
fig.add_trace(go.Scatter(x=treasury.treasury_data.index,
                         y=treasury.treasury_data['EFFR'],
                         mode='lines', name='EFFR', line=dict(color='red')))
fig.update_layout(xaxis_title='Date', yaxis_title='Rate (%)')
st.plotly_chart(fig, use_container_width=True)

# --- Yield Curve Spread ---
st.subheader("Yield Curve Spread (10Y - 2Y)")
fig = go.Figure()
fig.add_trace(go.Scatter(x=treasury.treasury_data.index,
                         y=treasury.treasury_data['Yield_Spread'],
                         mode='lines', name='10Y-2Y Spread', line=dict(color='blue')))
fig.add_hline(y=0, line_dash="dash", line_color="black")
fig.update_layout(xaxis_title='Date', yaxis_title='Spread (Percentage Points)')
st.plotly_chart(fig, use_container_width=True)

# --- 30-Year Mortgage Rate ---
st.subheader("30-Year Fixed Mortgage Rate")
fig = go.Figure()
fig.add_trace(go.Scatter(x=treasury.mortgage_data.index,
                         y=treasury.mortgage_data['30Y_Mortgage_Rate'],
                         mode='lines', name='30Y Mortgage Rate', line=dict(color='green')))
fig.update_layout(xaxis_title='Date', yaxis_title='Rate (%)')
st.plotly_chart(fig, use_container_width=True)

# ------------------- CPI -------------------
st.header("CPI - Year-over-Year Inflation")
cpi = CpiData()
cpi.fetch()
cpi.clean()
fig = go.Figure()
fig.add_trace(go.Scatter(x=cpi.data.index,
                         y=cpi.data['YoY_Inflation'],
                         mode='lines', name='YoY CPI Inflation', line=dict(color='green')))
fig.update_layout(xaxis_title='Date', yaxis_title='Inflation Rate (%)')
st.plotly_chart(fig, use_container_width=True)

# ------------------- Stock Indexes -------------------
st.header("Major U.S. Stock Indexes (Normalized)")
indexes = IndexData()
indexes.fetch()
indexes.clean()
fig = go.Figure()
for col in indexes.data.columns:
    fig.add_trace(go.Scatter(x=indexes.data.index, y=indexes.data[col], mode='lines', name=col))
fig.update_layout(xaxis_title='Date', yaxis_title='Index Level (Normalized to 100)')
st.plotly_chart(fig, use_container_width=True)