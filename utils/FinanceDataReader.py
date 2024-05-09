import requests
from requests import Response
import typing
from datetime import datetime, timedelta
import pandas as pd
import pytz 
from urllib.parse import urlencode, urljoin
import io

class FinanceDataReader:
    """
    A class that fetches historical financial data, using Yahoo Finance as the data provider. 
    """
  
    def __init__(self):
        self.base_url = "https://query1.finance.yahoo.com/v7/finance/download/"
        self.check_heartbeat()

    @staticmethod
    def print_error(response: Response) -> None:
        print(f"Request to {response.url} errored with status code {response.status_code}")
    
    def check_heartbeat(self) -> None:
        YAHOO_FINANCE_URL = "https://finance.yahoo.com/"
        response = requests.get(YAHOO_FINANCE_URL)
        if response.status_code != 200:
            self.print_error(response)
            raise Exception(f"Unable to reach {self.base_url}!")
        print("FinanceDataReader heartbeat check successful!")
    
    def _get_url(
        self,
        ticker: str,
        start_date: str,
        end_date: str,
        interval: str,
    ) -> str: 
        """
        Helper function for get_historical_data() to generate the URL for CSV data. 
        Parameters: 
            Same as get_historical_data(), except start_date and end_date have been 
            converted to UTC timestamps. 
        Returns: 
            URL of the historical data  
        """
        history_url = urljoin(self.base_url, ticker)
        query_params = {
            'period1': start_date,
            'period2': end_date,
            'interval': interval,
            'filter': 'history',
            'frequency': interval
        }
        url = f"{history_url}?{urlencode(query_params)}"
        return url

    def get_historical_data(
        self, 
        ticker: str,
        start_date: str = None,
        end_date: str = None,
        interval: str = "1d",
    ) -> pd.DataFrame:
        """
        Retrieve historical data (open/high/low/close price + volume) for a ticker.

        Parameters:
            ticker (str): The ticker to fetch data for 
            start_date (str): The starting date for the data, formatted as YYYYMMDD. 
                              Defaults to today - 1 Year. 
            end_date (str): The ending date for the data, formatted as YYYYMMDD. 
                            Defaults to today.   
            interval (str): The frequency of the data (e.g. "1d" for daily). 
                            Defaults to "1d". 
        
        Returns: A pandas DataFrame containing the time-series data. 
        """
        def _convert_to_timestamp(date):
            dt = datetime.strptime(date, "%Y%m%d")
            utc_zone = pytz.utc
            dt_obj = utc_zone.localize(dt)
            ts = int(dt_obj.timestamp())
            return str(ts)
        
        if end_date is None:
            today = datetime.now(pytz.utc)
            end_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = int(end_date.timestamp())
            end_date = str(end_date)
        else:
            end_date = _convert_to_timestamp(end_date)
        
        if start_date is None:
            today = datetime.now(pytz.utc)
            today_midnight = today.replace(hour=0, minute=0, second=0, microsecond=0)
            start_date = int((today_midnight - timedelta(days=365)).timestamp())
            start_date = str(start_date)
        else:
            start_date = _convert_to_timestamp(start_date)
        
        url = self._get_url(ticker, start_date, end_date, interval)
        headers = {
            'User-Agent': 'curl/7.64.1'
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = io.StringIO(response.text)
        else:
            self.print_error(response)
            raise Exception(f"Failed to download historical data for ticker {ticker}!")
        
        df = pd.read_csv(data)
        df.set_index("Date", inplace=True)
        return df

if __name__ == "__main__":
    data_reader = FinanceDataReader()
    df = data_reader.get_historical_data("AAPL")
    print(df)
