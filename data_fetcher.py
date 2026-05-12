"""
Functions to fetch energy price data from public APIs.
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st


class EIADataFetcher:
    """Fetches data from U.S. Energy Information Administration API."""
    
    BASE_URL = "https://api.eia.gov/series"
    
    # Gasoline price series IDs by state (weekly data)
    # Format: PET.EMM_EPM0_PTE_S{STATE}_DPG.W
    
    # Electricity retail price series IDs by state (annual data)
    # Format: ELEC.PRICE.{STATE}-RES.A
    
    STATE_ABBREV = {
        'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
        'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
        'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho',
        'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas',
        'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
        'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
        'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
        'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
        'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma',
        'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
        'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
        'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia',
        'WI': 'Wisconsin', 'WY': 'Wyoming', 'DC': 'District of Columbia'
    }
    
    def __init__(self, api_key):
        self.api_key = api_key
    
    def fetch_gasoline_prices(self):
        """
        Fetch weekly gasoline prices by state (most recent week).
        Returns DataFrame with state, price ($/gallon), and date.
        """
        data = []
        
        for state_code, state_name in self.STATE_ABBREV.items():
            series_id = f"PET.EMM_EPM0_PTE_S{state_code}_DPG.W"
            
            try:
                response = requests.get(
                    self.BASE_URL,
                    params={
                        'api_key': self.api_key,
                        'series_id': series_id,
                        'limit': 1  # Get most recent data point
                    },
                    timeout=5
                )
                response.raise_for_status()
                result = response.json()
                
                if 'series' in result and len(result['series']) > 0:
                    series_data = result['series'][0]
                    if 'data' in series_data and len(series_data['data']) > 0:
                        latest = series_data['data'][0]  # Most recent first
                        date_str, price = latest
                        
                        # Convert date from YYYYMMDD to datetime
                        date_obj = datetime.strptime(date_str, '%Y%m%d')
                        
                        data.append({
                            'state': state_code,
                            'state_name': state_name,
                            'price': float(price),
                            'date': date_obj,
                            'fuel_type': 'Gasoline'
                        })
            except Exception as e:
                st.warning(f"Could not fetch data for {state_name}: {str(e)}")
                continue
        
        return pd.DataFrame(data) if data else pd.DataFrame()
    
    def fetch_electricity_prices(self):
        """
        Fetch annual electricity prices by state (residential).
        Returns DataFrame with state, price (cents/kWh), and year.
        """
        data = []
        
        for state_code, state_name in self.STATE_ABBREV.items():
            series_id = f"ELEC.PRICE.{state_code}-RES.A"
            
            try:
                response = requests.get(
                    self.BASE_URL,
                    params={
                        'api_key': self.api_key,
                        'series_id': series_id,
                        'limit': 1
                    },
                    timeout=5
                )
                response.raise_for_status()
                result = response.json()
                
                if 'series' in result and len(result['series']) > 0:
                    series_data = result['series'][0]
                    if 'data' in series_data and len(series_data['data']) > 0:
                        latest = series_data['data'][0]
                        year_str, price = latest
                        
                        data.append({
                            'state': state_code,
                            'state_name': state_name,
                            'price': float(price),  # cents/kWh
                            'year': int(year_str),
                            'fuel_type': 'Electricity'
                        })
            except Exception as e:
                st.warning(f"Could not fetch electricity data for {state_name}: {str(e)}")
                continue
        
        return pd.DataFrame(data) if data else pd.DataFrame()


def get_mock_data():
    """
    Returns mock data for testing without an API key.
    Useful for development and demo purposes.
    """
    states = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
              'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
              'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
              'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
              'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY', 'DC']
    
    import random
    random.seed(42)
    
    gas_data = []
    for state in states:
        gas_data.append({
            'state': state,
            'price': random.uniform(2.5, 4.5),
            'fuel_type': 'Gasoline'
        })
    
    elec_data = []
    for state in states:
        elec_data.append({
            'state': state,
            'price': random.uniform(10, 20),
            'fuel_type': 'Electricity'
        })
    
    return pd.DataFrame(gas_data), pd.DataFrame(elec_data)
