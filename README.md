# Systematic Strategy Backtesting 

Tests the performance of systematic trading strategies using historical data, and provides/visualizes statistics such as P&L, portfolio value, risk (calculated as estimated tail loss), volatility (standard deviation of returns over the duration of the investment), mean return percentage, etc. 

### Sample Usage
Code is provided inside `main.py`. Suppose we are trying to test performance of a EWMA crossover strategy (9/21 day for fast/slow windows) for a single stock `MSFT`. 

![image](https://github.com/jeffreykaili/systematic-backtest/assets/57923095/4bae3b0e-9f21-44f7-94b3-864b609dad75)

With a few lines of code, we can backtest how this strategy would have performed over the last year: 

```python
from utils.FinanceDataReader import FinanceDataReader
from utils.EWMACrossoverStrategy import EWMACrossover
from Backtest import Backtest

data_reader = FinanceDataReader()
df = data_reader.get_historical_data("MSFT")
bt = Backtest(EWMACrossover, df, column_name='Close')
bt.run()
```

![image](https://github.com/jeffreykaili/systematic-backtest/assets/57923095/bbac21a7-27ed-45ad-ae56-1c52f0d8a3b8)
![image](https://github.com/jeffreykaili/systematic-backtest/assets/57923095/378f0ef4-e7c5-4a58-b142-a6ba48b291bf)

Additional statistics are printed to the console, such as mean return, estimated tail loss, and volatility.
