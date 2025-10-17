from fredapi import Fred
import yfinance as yf
import pandas as pd
import requests
import json

#Base Class
class MarketData:
    def __init__(self, name):
        self.name = name
        self.data = None

    def fetch(self):
        raise NotImplementedError("Subclasses must implement this method.")

    def clean(self):
        raise NotImplementedError("Subclasses must implement this method.")

#Treasury and EFFR data
class TreasuryData:
    def __init__(self, api_key):
        self.name = 'Treasury Yields & EFFR'
        self.fred = Fred(api_key=api_key)
        self.treasury_data = None
        self.mortgage_data = None

    # ------------------- Fetch Data -------------------
    def fetch(self):
        """Fetch 2Y, 10Y Treasury yields, EFFR, and 30Y fixed mortgage rate"""
        # Treasury & EFFR
        self.treasury_data = pd.DataFrame({
            '2Y_Treasury_Yield': self.fred.get_series('DGS2'),
            '10Y_Treasury_Yield': self.fred.get_series('DGS10'),
            'EFFR': self.fred.get_series('EFFR')
        })
        self.treasury_data.dropna(inplace=True)
        self.treasury_data.index = pd.to_datetime(self.treasury_data.index)
        self.treasury_data.sort_index(inplace=True)
        self.treasury_data['Yield_Spread'] = (
            self.treasury_data['10Y_Treasury_Yield'] - self.treasury_data['2Y_Treasury_Yield']
        )

        # 30-Year Fixed Mortgage
        self.mortgage_data = pd.DataFrame({
            '30Y_Mortgage_Rate': self.fred.get_series('MORTGAGE30US')
        })
        self.mortgage_data.dropna(inplace=True)
        self.mortgage_data.index = pd.to_datetime(self.mortgage_data.index)
        self.mortgage_data.sort_index(inplace=True)

#CPI data
class CpiData(MarketData):
    def __init__(self):
        super().__init__('CPI (Consumer Price Index)')

    def fetch(self, start_year="2010", end_year="2025"):
        """Fetch CPI data (All Urban Consumers, All Items) from BLS API"""
        headers = {'Content-type': 'application/json'}
        data = json.dumps({
            "seriesid": ['CUUR0000SA0'],  # CPI-U, All Items
            "startyear": start_year,
            "endyear": end_year
        })
        response = requests.post(
            'https://api.bls.gov/publicAPI/v1/timeseries/data/',
            data=data,
            headers=headers
        )
        json_data = response.json()

        # Extract CPI data
        records = []
        for series in json_data['Results']['series']:
            for item in series['data']:
                year = int(item['year'])
                period = item['period']
                value = float(item['value'])
                if period.startswith("M"):  # monthly data
                    month = int(period[1:])
                    date = pd.Timestamp(year=year, month=month, day=1)
                    records.append((date, value))

        # Convert to DataFrame
        self.data = pd.DataFrame(records, columns=['Date', 'CPI'])
        self.data.set_index('Date', inplace=True)
        self.data.sort_index(inplace=True)

    def clean(self):
        """Compute year-over-year CPI inflation rate (%)"""
        self.data['YoY_Inflation'] = self.data['CPI'].pct_change(12) * 100  # 12-month change
        self.data.dropna(inplace=True)

#Index Data
class IndexData(MarketData):
    def __init__(self):
        super().__init__('Major U.S. Stock Indexes')

    def fetch(self):
        """Fetch DJIA, S&P 500, and NASDAQ Composite data for the last 10 years"""
        tickers = {
            'DJIA': '^DJI',
            'S&P 500': '^GSPC',
            'NASDAQ': '^IXIC'
        }

        data = {}
        for name, ticker in tickers.items():
            df = yf.download(ticker, period="10y", interval="1d", auto_adjust=True)

            # Handle MultiIndex columns (some yfinance versions return these)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            # Use Adjusted Close if available, else Close
            col = 'Adj Close' if 'Adj Close' in df.columns else 'Close'
            data[name] = df[col]

        self.data = pd.DataFrame(data)
        self.data.dropna(inplace=True)

    def clean(self):
        """Normalize index values to start at 100 for comparison"""
        self.data = (self.data / self.data.iloc[0]) * 100