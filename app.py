"""
Streamlit app for visualizing USA energy prices (gas vs electricity) on an interactive map.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import json
import requests
from data_fetcher import EIADataFetcher, get_mock_data

# Page configuration
st.set_page_config(
    page_title="USA Energy Prices Map",
    page_icon="⛽",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("⛽ USA Energy Prices Map")
st.markdown("Compare gasoline and electricity prices across the USA")

# Sidebar for controls
st.sidebar.header("Configuration")

# API Key input
use_mock_data = st.sidebar.checkbox("Use mock data (no API key needed)", value=True)

if not use_mock_data:
    api_key = st.sidebar.text_input("Enter EIA API Key", type="password", 
                                     help="Get your free API key at https://www.eia.gov/opendata/")
else:
    api_key = None

# Data source selection
price_type = st.sidebar.radio(
    "Select price type:",
    ["Gasoline ($/gallon)", "Electricity (cents/kWh)"],
    help="Toggle between fuel types"
)

# Load data
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data(use_mock, api_key_val):
    """Fetch energy price data."""
    if use_mock:
        st.info("📊 Using mock data for demonstration")
        gas_df, elec_df = get_mock_data()
        return gas_df, elec_df
    else:
        if not api_key_val:
            st.error("Please provide an EIA API key or use mock data")
            return None, None
        
        with st.spinner("Fetching data from EIA..."):
            fetcher = EIADataFetcher(api_key_val)
            gas_df = fetcher.fetch_gasoline_prices()
            elec_df = fetcher.fetch_electricity_prices()
        
        return gas_df, elec_df

# Fetch the data
gas_prices, elec_prices = load_data(use_mock_data, api_key)

if gas_prices is None or elec_prices is None:
    st.error("Failed to load data. Please try again.")
    st.stop()

# Select which data to display
if "Gasoline" in price_type:
    df = gas_prices.copy()
    color_col = "price"
    title = "Gasoline Prices by State"
    unit = "$/gallon"
else:
    df = elec_prices.copy()
    color_col = "price"
    title = "Electricity Prices by State"
    unit = "cents/kWh"

# Load US state GeoJSON
@st.cache_data
def load_geojson():
    """Load GeoJSON for US states."""
    url = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
    try:
        # For this prototype, we'll use a simpler approach with state centroids
        return None
    except:
        return None

# Create choropleth map using Plotly
# First, we need state FIPS codes for the choropleth
state_fips = {
    'AL': 1, 'AK': 2, 'AZ': 4, 'AR': 5, 'CA': 6, 'CO': 8, 'CT': 9, 'DE': 10,
    'FL': 12, 'GA': 13, 'HI': 15, 'ID': 16, 'IL': 17, 'IN': 18, 'IA': 19, 'KS': 20,
    'KY': 21, 'LA': 22, 'ME': 23, 'MD': 24, 'MA': 25, 'MI': 26, 'MN': 27, 'MS': 28,
    'MO': 29, 'MT': 30, 'NE': 31, 'NV': 32, 'NH': 33, 'NJ': 34, 'NM': 35, 'NY': 36,
    'NC': 37, 'ND': 38, 'OH': 39, 'OK': 40, 'OR': 41, 'PA': 42, 'RI': 44, 'SC': 45,
    'SD': 46, 'TN': 47, 'TX': 48, 'UT': 49, 'VT': 50, 'VA': 51, 'WA': 53, 'WV': 54,
    'WI': 55, 'WY': 56, 'DC': 11
}

df['fips'] = df['state'].map(state_fips)

# Create choropleth
fig = px.choropleth(
    df,
    locations='state',
    locationmode='USA-states',
    color='price',
    hover_name='state',
    hover_data={
        'state': False,
        'price': f':.2f'
    },
    color_continuous_scale='RdYlGn_r',  # Red (high) to Green (low)
    scope='usa',
    title=title,
    labels={'price': unit}
)

fig.update_geos(
    projection_type='albers usa',
    showland=True,
    landcolor='rgb(243, 243, 243)',
    coastcolor='rgb(204, 204, 204)',
    countrycolor='rgb(204, 204, 204)',
)

fig.update_layout(
    title_x=0.5,
    height=600,
    geo=dict(
        showlakes=True,
        lakecolor='rgb(255, 255, 255)',
    )
)

st.plotly_chart(fig, use_container_width=True)

# Display statistics
st.subheader("📊 Statistics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Highest Price",
        f"{df['price'].max():.2f} {unit}",
        df[df['price'] == df['price'].max()]['state'].values[0]
    )

with col2:
    st.metric(
        "Lowest Price",
        f"{df['price'].min():.2f} {unit}",
        df[df['price'] == df['price'].min()]['state'].values[0]
    )

with col3:
    st.metric(
        "Average Price",
        f"{df['price'].mean():.2f} {unit}"
    )

with col4:
    st.metric(
        "Price Variance",
        f"${df['price'].std():.2f} {unit}"
    )

# Display table
st.subheader("📋 State-by-State Breakdown")
display_df = df[['state_name' if 'state_name' in df.columns else 'state', 'price']].sort_values('price', ascending=False)
if 'state_name' in df.columns:
    display_df = display_df.rename(columns={'state_name': 'State'})
else:
    display_df = display_df.rename(columns={'state': 'State'})
display_df = display_df.rename(columns={'price': f'Price ({unit})'})
display_df[f'Price ({unit})'] = display_df[f'Price ({unit})'].round(2)

st.dataframe(display_df, use_container_width=True)

# Footer
st.divider()
st.caption("""
**Data Sources:**
- Gasoline prices: U.S. Energy Information Administration (EIA) API
- Electricity prices: U.S. Energy Information Administration (EIA) API

**Note:** This is a prototype using state-level data. County-level data aggregation coming soon.
""")
