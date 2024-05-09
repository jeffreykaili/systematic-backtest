from utils.FinanceDataReader import FinanceDataReader
from utils.EWMACrossoverStrategy import EWMACrossover
from Backtest import Backtest

data_reader = FinanceDataReader()
df = data_reader.get_historical_data("MSFT")
bt = Backtest(EWMACrossover, df, column_name='Close')
bt.run()
